"""
Milvus 导入节点 - 将切片后的文本和向量存入 Milvus
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
from pymilvus import MilvusClient, DataType

from processor.import_process.base import BaseNode, setup_logging
from processor.import_process.exceptions import StateFieldError, ValidationError, MilvusError
from utils.storage_clients import StorageClients


@dataclass
class _SCALAR_FIELD_SPC:
    """标量字段规范"""
    field_name: str
    datatype: DataType
    max_length: Optional[int] = None


# 定义所有标量字段
_SCALAR_FIELDS: [_SCALAR_FIELD_SPC] = (
    _SCALAR_FIELD_SPC(field_name="content", datatype=DataType.VARCHAR, max_length=65535),
    _SCALAR_FIELD_SPC(field_name="title", datatype=DataType.VARCHAR, max_length=65535),
    _SCALAR_FIELD_SPC(field_name="parent_title", datatype=DataType.VARCHAR, max_length=65535),
    _SCALAR_FIELD_SPC(field_name="file_title", datatype=DataType.VARCHAR, max_length=65535),
    _SCALAR_FIELD_SPC(field_name="item_name", datatype=DataType.VARCHAR, max_length=65535),
)


class _MilvusSchemaBuilder:
    """Milvus Schema 构建器"""

    @staticmethod
    def build_schema(milvus_client: MilvusClient, dim: int):
        """
        创建 schema

        Args:
            milvus_client: Milvus 客户端
            dim: 向量维度

        Returns:
            schema: Milvus 集合 schema
        """
        # 1. 创建 schema（启用动态字段）
        schema = milvus_client.create_schema(enable_dynamic_field=True)

        # 2. ���加字段约束
        # 2.1 添加主键字段（自动生成 ID）
        schema.add_field(
            field_name="chunk_id",
            datatype=DataType.INT64,
            is_primary=True,
            auto_id=True
        )

        # 2.2 添加向量字段
        schema.add_field(
            field_name="dense_vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=dim
        )
        schema.add_field(
            field_name="sparse_vector",
            datatype=DataType.SPARSE_FLOAT_VECTOR
        )

        # 2.3 添加标量字段
        for spec in _SCALAR_FIELDS:
            kwargs: Dict = {
                "field_name": spec.field_name,
                "datatype": spec.datatype
            }
            if spec.max_length:
                kwargs['max_length'] = spec.max_length

            schema.add_field(**kwargs)

        return schema


class _MilvusInserter:
    """Milvus 数据插入器"""

    def __init__(self, milvus_client: MilvusClient, collection_name: str):
        self._milvus_client = milvus_client
        self._collection_name = collection_name

    def insert_rows(self, data: List[Dict[str, Any]]):
        """
        批量插入数据

        Args:
            data: 待插入的数据列表
        """
        # 1. 插入数据
        inserted_result = self._milvus_client.insert(
            collection_name=self._collection_name,
            data=data
        )

        # 2. 获取每个 chunk 的 ID
        chunk_ids = inserted_result.get('ids')

        # 3. 回填 ID 到 chunk 中
        for chunk_id, chunk in zip(chunk_ids, data):
            chunk['chunk_id'] = chunk_id


class _MilvusIndexBuilder:
    """Milvus 索引构建器"""

    @staticmethod
    def build_index_params(milvus_client: MilvusClient):
        """
        构建索引参数

        Args:
            milvus_client: Milvus 客户端

        Returns:
            index_params: 索引参数
        """
        index = milvus_client.prepare_index_params()

        # 稠密向量：AUTOINDEX
        index.add_index(
            field_name="dense_vector",
            index_name="dense_vector_index",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )

        # 稀疏向量：倒排索引
        index.add_index(
            field_name="sparse_vector",
            index_name="sparse_vector_index",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="IP"
        )

        return index


class ImportMilvusNode(BaseNode):
    """
    Milvus 导入节点（门面模式）

    负责：
    1. 校验输入状态
    2. 获取 Milvus 客户端
    3. 创建集合（如不存在）
    4. 插入数据并回填 ID
    """

    name = "import_milvus_node"

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理导入状态

        Args:
            state: 导入状态字典

        Returns:
            Dict[str, Any]: 更新后的状态字典
        """
        # 1. 校验 state
        validated_chunks, dim = self._validate_state(state)

        # 2. 获取 Milvus 客户端
        try:
            milvus_client = StorageClients.get_milvus_client()
        except ConnectionError as e:
            self.logger.error(f"Milvus 客户端创建失败，异常原因：{str(e)}")
            raise MilvusError(
                message=f"Milvus 客户端创建失败，异常原因：{str(e)}",
                node_name=self.name
            )

        # 3. 获取 chunks 集合名称
        chunks_collection = self.config.chunks_collection

        # 4. 创建集合（如不存在）
        self._create_chunks_collection(chunks_collection, milvus_client, dim)

        # 5. 插入数据
        _inserter = _MilvusInserter(milvus_client, chunks_collection)
        _inserter.insert_rows(validated_chunks)

        # 6. 更新 state
        state['chunks'] = validated_chunks
        self.logger.info(f"成功插入 {len(validated_chunks)} 个 chunks 到 Milvus")

        # 7. 返回 state
        return state

    def _validate_state(self, state: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """
        校验状态数据

        Args:
            state: 输入状态

        Returns:
            Tuple[List[Dict[str, Any]], int]: (有效的 chunks 列表, 向量维度)

        Raises:
            StateFieldError: 状态字段异常
            ValidationError: 数据验证异常
        """
        self.log_step("validate", "开始参数校验")

        chunks = state.get("chunks")
        if not chunks or not isinstance(chunks, list):
            raise StateFieldError("待入库的 chunks 为空或类型无效", self.name)

        validated_chunks = []
        for i, chunk in enumerate(chunks):
            # 类型不对 → 抛异常
            if not isinstance(chunk, dict):
                raise ValidationError(
                    f"chunks[{i}] 类型无效：期望 dict，实际为 {type(chunk).__name__}",
                    self.name
                )

            # 缺少向量 → 跳过（数据级容错）
            if chunk.get("dense_vector") and chunk.get("sparse_vector"):
                validated_chunks.append(chunk)
            else:
                self.logger.warning(f"chunks[{i}] 缺少混合向量，已跳过")

        if not validated_chunks:
            raise ValidationError("所有 chunk 均无有效向量，无法入库", self.name)

        dim = len(validated_chunks[0]["dense_vector"])
        self.logger.info(f"有效 chunks：{len(validated_chunks)}，向量维度：{dim}")

        return validated_chunks, dim

    def _create_chunks_collection(
        self,
        chunks_collection: str,
        milvus_client: MilvusClient,
        dim: int
    ):
        """
        创建 chunks 集合

        Args:
            chunks_collection: 集合名称
            milvus_client: Milvus 客户端
            dim: 向量维度
        """
        # 1. 检查集合是否已存在
        if milvus_client.has_collection(chunks_collection):
            self.logger.info(f"{chunks_collection} 已存在，跳过创建")
            return

        # 2. 创建 schema
        self.log_step("schema", "开始构建 schema")
        schema = _MilvusSchemaBuilder.build_schema(milvus_client, dim)

        # 3. 创建索引
        self.log_step("index", "开始构建索引")
        index_params = _MilvusIndexBuilder.build_index_params(milvus_client)

        # 4. 创建集合
        self.log_step("collection", f"开始创建集合 {chunks_collection}")
        milvus_client.create_collection(
            collection_name=chunks_collection,
            schema=schema,
            index_params=index_params
        )

        self.logger.info(f"集合 {chunks_collection} 创建成功")


def _cli_main() -> None:
    """命令行测试入口"""
    import json
    from pathlib import Path

    setup_logging()

    # 测试数据路径
    temp_dir = Path(__file__).parent.parent / "temp_dir"
    input_path = temp_dir / "chunks_vector.json"
    output_path = temp_dir / "chunks_vector_ids.json"

    if not input_path.exists():
        print(f"⚠️  找不到测试文件: {input_path}")
        print("请准备测试数据或修改路径")
        return

    # 读取测试数据
    with open(input_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    state: Dict[str, Any] = {"chunks": content.get('chunks', [])}

    # 执行节点
    node = ImportMilvusNode()
    try:
        result_state = node.process(state)

        # 保存结果
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_state, f, ensure_ascii=False, indent=4)

        print(f"✅ 结果已保存至: {output_path}")

    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        raise


if __name__ == '__main__':
    _cli_main()
