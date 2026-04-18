# ImportMilvusNode 使用说明

## 📋 概述

`ImportMilvusNode` 是一个用于将文本切片和向量数据导入 Milvus 向量数据库的节点。它是 Babycare 育儿知识库 Import 流程的核心组件之一。

## 🏗️ 架构设计

### 核心组件

1. **ImportMilvusNode**（门面类）
   - 统一的入口，协调整个导入流程
   - 继承自 `BaseNode`
   - 实现 `process(state)` 方法

2. **_MilvusSchemaBuilder**（Schema 构建器）
   - 定义集合结构
   - 配置主键、向量字段、标量字段

3. **_MilvusIndexBuilder**（索引构建器）
   - 构建稠密向量索引（AUTOINDEX + COSINE）
   - 构建稀疏向量索引（SPARSE_INVERTED_INDEX + IP）

4. **_MilvusInserter**（数据插入器）
   - 批量插入数据
   - 自动回填生成的 ID

### 数据字段

#### 主键字段
- `chunk_id`: INT64，自动生成，主键

#### 向量字段
- `dense_vector`: FLOAT_VECTOR，稠密向量
- `sparse_vector`: SPARSE_FLOAT_VECTOR，稀疏向量

#### 标量字段
- `content`: VARCHAR(65535)，文本内容
- `title`: VARCHAR(65535)，标题
- `parent_title`: VARCHAR(65535)，父级标题
- `file_title`: VARCHAR(65535)，文件标题
- `item_name`: VARCHAR(65535)，项目名称

## 🚀 使用方法

### 1. 环境准备

#### 安装依赖
```bash
pip install pymilvus
```

#### 配置 Milvus
在 `.env` 文件中配置：
```bash
MILVUS_URL=http://127.0.0.1:19530
CHUNKS_COLLECTION=kb_chunks_v1
```

### 2. 数据格式

输入状态中的 `chunks` 应该是以下格式：

```python
state = {
    "chunks": [
        {
            "content": "文本内容",
            "title": "标题",
            "parent_title": "父级标题",
            "file_title": "文件标题",
            "item_name": "项目名称",
            "dense_vector": [0.1, 0.2, ...],  # 稠密向量
            "sparse_vector": {0: 0.5, 10: 0.8}  # 稀疏向量
        },
        # ... 更多 chunks
    ]
}
```

### 3. 基本使用

```python
from processor.import_process.nodes.import_milvus import ImportMilvusNode

# 创建节点实例
node = ImportMilvusNode()

# 准备状态
state = {
    "chunks": [...]  # 你的数据
}

# 执行导入
try:
    result_state = node.process(state)
    print(f"✅ 成功导入 {len(result_state['chunks'])} 个 chunks")
except Exception as e:
    print(f"❌ 导入失败: {str(e)}")
```

### 4. 集成到 Import 流程

在 `processor/import_process/main_graph.py` 中添加节点：

```python
from processor.import_process.nodes.import_milvus import ImportMilvusNode

# 创建节点实例
import_milvus_node = ImportMilvusNode()

# 添加到工作流
workflow.add_node("import_milvus", import_milvus_node.process)
```

## 🔧 高级配置

### 修改字段定义

编辑 `_SCALAR_FIELDS` 来添加或修改标量字段：

```python
_SCALAR_FIELDS: [_SCALAR_FIELD_SPC] = (
    _SCALAR_FIELD_SPC(field_name="content", datatype=DataType.VARCHAR, max_length=65535),
    # 添加你的自定义字段
    _SCALAR_FIELD_SPC(field_name="custom_field", datatype=DataType.VARCHAR, max_length=1024),
)
```

### 修改索引类型

编辑 `_MilvusIndexBuilder.build_index_params()` 来调整索引：

```python
# 修改稠密向量索引
index.add_index(
    field_name="dense_vector",
    index_name="dense_vector_index",
    index_type="IVF_FLAT",  # 改为其他索引类型
    metric_type="COSINE"
)
```

## 🧪 测试

### 命令行测试

```bash
# 准备测试数据
cat > processor/import_process/temp_dir/chunks_vector.json << EOF
{
  "chunks": [
    {
      "content": "测试内容",
      "title": "测试标题",
      "dense_vector": [0.1, 0.2, 0.3],
      "sparse_vector": {0: 0.5, 1: 0.8}
    }
  ]
}
EOF

# 运行测试
python processor/import_process/nodes/import_milvus.py
```

### 单元测试

```python
import pytest
from processor.import_process.nodes.import_milvus import ImportMilvusNode

def test_import_milvus_node():
    node = ImportMilvusNode()
    state = {
        "chunks": [
            {
                "content": "测试",
                "dense_vector": [0.1] * 768,
                "sparse_vector": {i: 0.1 for i in range(10)}
            }
        ]
    }

    result = node.process(state)
    assert 'chunks' in result
    assert len(result['chunks']) > 0
```

## 📊 日志输出

节点运行时会输出详细的日志：

```
[ImportMilvusNode] [validate] 开始参数校验
[ImportMilvusNode] 有效 chunks：10，向量维度：768
[ImportMilvusNode] [schema] 开始构建 schema
[ImportMilvusNode] [index] 开始构建索引
[ImportMilvusNode] [collection] 开始创建集合 kb_chunks_v1
[ImportMilvusNode] 集合 kb_chunks_v1 创建成功
[ImportMilvusNode] 成功插入 10 个 chunks 到 Milvus
```

## ⚠️ 异常处理

节点会抛出以下异常：

- `StateFieldError`: chunks 为空或类型无效
- `ValidationError`: 所有 chunk 均无有效向量
- `MilvusError`: Milvus 客户端创建失败

建议在调用时使用 try-except 捕获异常。

## 🔗 相关文件

- `processor/import_process/base.py`: BaseNode 基类
- `processor/import_process/exceptions.py`: 异常定义
- `utils/storage_clients.py`: Milvus 客户端管理
- `core/settings.py`: 配置管理

## 📝 注意事项

1. **向量维度一致性**：确保所有 chunks 的 dense_vector 维度相同
2. **稀疏向量格式**：稀疏向量应为字典格式 `{index: value}`
3. **字段完整性**：虽然启用了动态字段，但建议提供所有标量字段
4. **集合已存在**：如果集合已存在，会跳过创建，直接插入数据
5. **ID 回填**：插入成功后，chunk_id 会自动回填到原始数据中

## 🎯 性能优化

1. **批量插入**：节点支持批量插入，建议每次插入 100-1000 个 chunks
2. **索引选择**：根据数据规模选择合适的索引类型
3. **连接复用**：Milvus 客户端使用单例模式，自动复用连接
