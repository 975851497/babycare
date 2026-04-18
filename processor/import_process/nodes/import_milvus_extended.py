"""
Milvus 导入节点 - 将切片后的文本和向量存入 Milvus (扩展版本)
包含新的元数据字段支持
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
from pymilvus import MilvusClient, DataType

from processor.import_process.base import BaseNode, setup_logging
from processor.import_process.exceptions import StateFieldError, ValidationError, MilvusError
from utils.client.storage_clients import StorageClients


@dataclass
class _SCALAR_FIELD_SPC:
    """标量字段规范"""
    field_name: str
    datatype: DataType
    max_length: Optional[int] = None
    description: Optional[str] = None  # 新增：字段描述


# 定义扩展的标量字段（包含业务需求字段）
_EXTENDED_SCALAR_FIELDS: [_SCALAR_FIELD_SPC] = (
    # 基础字段
    _SCALAR_FIELD_SPC(
        field_name="content",
        datatype=DataType.VARCHAR,
        max_length=65535,
        description="正文内容"
    ),
    _SCALAR_FIELD_SPC(
        field_name="title",
        datatype=DataType.VARCHAR,
        max_length=65535,
        description="文章标题"
    ),

    # 新增：业务元数据字段
    _SCALAR_FIELD_SPC(
        field_name="content_type",
        datatype=DataType.VARCHAR,
        max_length=255,
        description="内容类型 (育儿建议/专家文章/沟通话术/亲子案例/知识科普)"
    ),
    _SCALAR_FIELD_SPC(
        field_name="author",
        datatype=DataType.VARCHAR,
        max_length=255,
        description="作者"
    ),
    _SCALAR_FIELD_SPC(
        field_name="age_group",
        datatype=DataType.VARCHAR,
        max_length=255,
        description="年龄段 (0-3岁/3-6岁/6-12岁/12-18岁/通用)"
    ),
    _SCALAR_FIELD_SPC(
        field_name="issue_type",
        datatype=DataType.VARCHAR,
        max_length=255,
        description="问题类型 (情绪管理/行为引导/沟通技巧/学习辅导/健康饮食/睡眠问题)"
    ),
    _SCALAR_FIELD_SPC(
        field_name="source_file",
        datatype=DataType.VARCHAR,
        max_length=65535,
        description="来源文件名"
    ),
)


class _MilvusSchemaBuilder:
    """Milvus Schema 构建器 (扩展版本)"""

    @staticmethod
    def build_extended_schema(milvus_client: MilvusClient, dim: int):
        """
        创建扩展版 schema（包含业务元数据字段）

        Args:
            milvus_client: Milvus 客户端
            dim: 向量维度

        Returns:
            schema: Milvus 集合 schema
        """
        # 1. 创建 schema（启用动态字段）
        schema = milvus_client.create_schema(enable_dynamic_field=True)

        # 2. 添加字段约束
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

        # 2.3 添加标量字段（扩展版）
        for spec in _EXTENDED_SCALAR_FIELDS:
            kwargs: Dict = {
                "field_name": spec.field_name,
                "datatype": spec.datatype
            }
            if spec.max_length:
                kwargs['max_length'] = spec.max_length

            schema.add_field(**kwargs)

        return schema


class _MilvusInserter:
    """Milvus 数据插入器 (扩展版本)"""

    def __init__(self, milvus_client: MilvusClient, collection_name: str):
        self._milvus_client = milvus_client
        self._collection_name = collection_name

    def insert_rows(self, data: List[Dict[str, Any]]):
        """
        批量插入数据

        Args:
            data: 待插入的数据列表（必须包含所有必需字段）
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


class ImportMilvusNodeExtended(BaseNode):
    """
    Milvus 导入节点 (扩展版本 - 支持业务元数据)

    负责：
    1. 校验输入状态
    2. 提取和填充业务元数据
    3. 获取 Milvus 客户端
    4. 创建扩展版集合（如不存在）
    5. 插入数据并回填 ID
    """

    name = "import_milvus_node_extended"

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理导入状态

        Args:
            state: 导入状态字典，必须包含：
                - chunks: List[str] - 切片文本
                - embeddings: List[List[float]] - 向量列表
                - metadata: Dict[str, str] - 元数据（可选）

        Returns:
            Dict[str, Any]: 更新后的状态字典
        """
        # 1. 校验并填充业务元数据
        validated_chunks, dim = self._validate_and_enrich_state(state)

        # 2. 获取 Milvus 客户端
        try:
            milvus_client = StorageClients.get_milvus_client()
        except ConnectionError as e:
            self.logger.error(f"Milvus 客户端创建失败，异常原因：{str(e)}")
            raise MilvusError(
                message=f"Milvus 客户端创建失败，异常原因：{str(e)}",
                node_name=self.name
            )

        # 3. 获取扩展版集合名称
        chunks_collection = self.config.chunks_collection + "_v2"  # 使用 v2 版本

        # 4. 创建扩展版集合（如不存在）
        self._create_extended_collection(chunks_collection, milvus_client, dim)

        # 5. 插入数据
        _inserter = _MilvusInserter(milvus_client, chunks_collection)
        _inserter.insert_rows(validated_chunks)

        # 6. 更新 state
        state['chunks'] = validated_chunks
        state['collection_name'] = chunks_collection  # 记录使用的集合名
        self.logger.info(f"成功插入 {len(validated_chunks)} 个 chunks 到 {chunks_collection}")

        # 7. 返回 state
        return state

    def _validate_and_enrich_state(self, state: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """
        校验状态数据并填充业务元数据

        Args:
            state: 输入状态

        Returns:
            Tuple[List[Dict[str, Any]], int]: (有效的 chunks 列表, 向量维度)

        Raises:
            StateFieldError: 状态字段异常
            ValidationError: 数据验证异常
        """
        self.log_step("validate", "开始参数校验和元数据填充")

        chunks = state.get("chunks")
        embeddings = state.get("embeddings")

        if not chunks or not isinstance(chunks, list):
            raise StateFieldError("待入库的 chunks 为空或类型无效", self.name)
        if not embeddings or not isinstance(embeddings, list):
            raise StateFieldError("embeddings 为空或类型无效", self.name)

        # 获取元数据（从state中提取或使用默认值）
        metadata = state.get("metadata", {})
        source_file = metadata.get("source_file", "未知文件")

        validated_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # 类型校验
            if not isinstance(chunk, str):
                raise ValidationError(
                    f"chunks[{i}] 类型无效：期望 str，实际为 {type(chunk).__name__}",
                    self.name
                )

            # 向量校验
            if not embedding or not isinstance(embedding, list):
                self.logger.warning(f"chunks[{i}] 缺少向量，已跳过")
                continue

            # 构建扩展版数据结构（包含所有业务元数据字段）
            enriched_chunk = {
                # 基础字段
                "content": chunk,
                "title": metadata.get("title", "未知标题"),
                "source_file": source_file,

                # 业务元数据字段（从metadata提取或使用默认值）
                "content_type": metadata.get("content_type", "育儿建议"),
                "author": metadata.get("author", "未知作者"),
                "age_group": metadata.get("age_group", "通用"),
                "issue_type": metadata.get("issue_type", "通用"),

                # 向量字段
                "dense_vector": embedding,
                # 生成简单的稀疏向量（MVP 版本）
                "sparse_vector": {j: float(v) for j, v in enumerate(embedding) if v > 0.5}
            }

            validated_chunks.append(enriched_chunk)

        if not validated_chunks:
            raise ValidationError("所有 chunk 均无效，无法入库", self.name)

        dim = len(validated_chunks[0]["dense_vector"])
        self.logger.info(f"有效 chunks：{len(validated_chunks)}，向量维度：{dim}")
        self.logger.info(f"业务元数据示例：content_type={validated_chunks[0]['content_type']}, "
                        f"age_group={validated_chunks[0]['age_group']}, "
                        f"issue_type={validated_chunks[0]['issue_type']}")

        return validated_chunks, dim

    def _create_extended_collection(
        self,
        chunks_collection: str,
        milvus_client: MilvusClient,
        dim: int
    ):
        """
        创建扩展版 chunks 集合

        Args:
            chunks_collection: 集合名称
            milvus_client: Milvus 客户端
            dim: 向量维度
        """
        # 1. 检查集合是否已存在
        if milvus_client.has_collection(chunks_collection):
            self.logger.info(f"{chunks_collection} 已存在，跳过创建")
            return

        # 2. 创建扩展版 schema
        self.log_step("schema", f"开始构建扩展版 schema ({chunks_collection})")
        schema = _MilvusSchemaBuilder.build_extended_schema(milvus_client, dim)

        # 3. 创建索引
        self.log_step("index", "开始构建索引")
        index_params = _MilvusIndexBuilder.build_index_params(milvus_client)

        # 4. 创建集合
        self.log_step("collection", f"开始创建扩展版集合 {chunks_collection}")
        milvus_client.create_collection(
            collection_name=chunks_collection,
            schema=schema,
            index_params=index_params
        )

        self.logger.info(f"扩展版集合 {chunks_collection} 创建成功")
        self.logger.info(f"新增字段：content_type, author, age_group, issue_type, source_file")


def _cli_main() -> None:
    """命令行测试入口"""
    import json
    from pathlib import Path

    setup_logging()

    # 测试数据路径
    temp_dir = Path(__file__).parent.parent.parent / "temp_dir"
    input_path = temp_dir / "chunks_vector.json"
    output_path = temp_dir / "chunks_vector_extended.json"

    if not input_path.exists():
        print(f"⚠️  找不到测试文件: {input_path}")
        print("请准备测试数据或修改路径")
        return

    # 读取测试数据
    with open(input_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    # 构建测试状态（包含元数据）
    state: Dict[str, Any] = {
        "chunks": content.get('chunks', []),
        "embeddings": content.get('embeddings', []),
        "metadata": {
            "content_type": "育儿建议",
            "author": "育儿专家",
            "age_group": "3-6岁",
            "issue_type": "情绪管理",
            "source_file": "test.md",
            "title": "测试文档"
        }
    }

    # 执行节点
    node = ImportMilvusNodeExtended()
    try:
        result_state = node.process(state)

        # 保存结果
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_state, f, ensure_ascii=False, indent=4)

        print(f"✅ 结果已保存至: {output_path}")
        print(f"📊 写入集合: {result_state.get('collection_name', 'N/A')}")
        print(f"📊 写入 chunks: {len(result_state.get('chunks', []))}")

    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        raise


if __name__ == '__main__':
    _cli_main()
