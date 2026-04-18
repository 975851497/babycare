# Import Process 结构规范说明

## 1. 统一的 State 结构

```python
class ImportState(TypedDict, total=False):
    # 输入
    file_path: str

    # 中间数据
    raw_text: str
    chunks: List[str]
    embeddings: List[List[float]]
    vector_ids: List[str]

    # 状态控制
    status: str  # "pending" | "completed" | "failed" | "success"
    error: Optional[str]

    # 元数据
    current_step: str  # 当前执行到哪个步骤
```

## 2. 节点标准实现规范

### ✅ 规范要求

1. **函数签名**: 所���节点必须接收 `state: Dict[str, Any]`
2. **返回值**: 必须返回 `Dict[str, Any]` 作为 state update
3. **状态管理**: 每个节点必须设置 `status` 和 `current_step`
4. **错误处理**: 失败时返回 `status: "failed"` 和 `error` 信息
5. **参数传递**: 严禁使用单独参数，只能通过 state 传递

### ✅ 标准节点模板

```python
def node_name(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    节点描述

    Args:
        state: 包含必要输入的状态字典

    Returns:
        state update dict
    """
    # 1. 参数校验
    input_data = state.get("input_key")
    if not input_data:
        return {
            "status": "failed",
            "error": "input_key 为空",
            "current_step": "node_name"
        }

    try:
        # 2. 业务逻辑
        output_data = process(input_data)

        # 3. 返回成功状态
        return {
            "output_key": output_data,
            "status": "success",
            "current_step": "node_name"
        }
    except Exception as e:
        # 4. 异常处理
        return {
            "status": "failed",
            "error": str(e),
            "current_step": "node_name"
        }
```

## 3. 当前节点列表

| 节点名称 | 功能 | 输入 | 输出 |
|---------|------|------|------|
| `parse_document` | 文档解析 | `file_path` | `raw_text` |
| `split_document` | 文本切分 | `raw_text` | `chunks` |
| `generate_embedding` | 向量生成 | `chunks` | `embeddings` |
| `vector_upsert` | 向量存储 | `embeddings`, `chunks` | `vector_ids` |

## 4. LangGraph 流程图

```
┌─────────────────────────────────────────────────────┐
│                    Import Pipeline                   │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   parse      │  解析文档
            └──────────────┘
                    │
                    ▼ (success)
            ┌──────────────┐
            │   split      │  切分文本
            └──────────────┘
                    │
                    ▼ (success)
            ┌──────────────┐
            │   embed      │  生成向量
            └──────────────┘
                    │
                    ▼ (success)
            ┌──────────────┐
            │   upsert     │  存储向量
            └──────────────┘
                    │
                    ▼
               completed
```

## 5. 使用方式

### 基本调用

```python
from processor.import_process.main_graph import run_import_pipeline

result = run_import_pipeline("/path/to/document.pdf")

if result["status"] == "completed":
    print(f"处理成功: {len(result['vector_ids'])} 个向量")
else:
    print(f"处理失败: {result['error']}")
```

### 直接调用单个节点

```python
from processor.import_process.nodes.parse_document import parse_document

state = {
    "file_path": "/path/to/document.pdf"
}

result = parse_document(state)

# result: {"raw_text": "...", "status": "success", "current_step": "parse_document"}
```

## 6. 错误处理机制

每个节点都遵循统一的错误处理模式：

1. **参数校验失败**: 返回 `status: "failed"` + 具体错误信息
2. **业务逻辑异常**: 捕获异常并返回 `status: "failed"` + 异常信息
3. **流程中断**: 通过条件边检测 `status: "failed"` 并提前终止

## 7. 扩展新节点

添加新节点时，请遵循以下步骤：

1. 在 `nodes/` 目录下创建新文件
2. 实现标准函数签名：`def new_node(state: Dict[str, Any]) -> Dict[str, Any]`
3. 确保返回包含 `status` 和 `current_step` 的字典
4. 在 `main_graph.py` 中注册节点并添加条件边
5. 更新本文档的节点列表

## 8. MVP 版本说明

当前实现为 MVP 版本，包含以下简化：

- **向量生成**: 简单的字符编码模拟，非真实 embedding
- **向量存储**: 内存字典模拟，非真实向量数据库
- **文本切分**: 基于固定长度的简单切分，非语义切分

生产环境需要替换为：
- 真实的 embedding 服务（如 OpenAI, Cohere）
- 真实的向量数据库（如 Pinecone, Milvus, Qdrant）
- 智能的文本切分策略（如基于语义、段落结构）
