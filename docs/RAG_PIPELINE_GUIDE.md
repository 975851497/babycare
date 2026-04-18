# Babycare 育儿知识库 - RAG流水线完整指南

## 📋 项目概述

本项目实现了一个完整的RAG（检索增强生成）流水线，用于为家长提供智能育儿建议。

### 🎯 核心功能

1. **混合向量检索**：使用BGE-M3模型进行稠密+稀疏向量检索
2. **HyDE检索**：假设性文档嵌入，解决查询-文档语义鸿沟
3. **联网检索**：通过MCP协议进行实时联网搜索（可选）
4. **RRF融合**：多路检索结果智能融合
5. **重排序**：BGE-Reranker精排，断崖截断去除低质文档
6. **答案生成**：基于精排上下文生成专业、温暖的育儿建议

---

## 🔧 环境准备

### 1. 系统要求

- Python 3.10+
- Milvus 2.3+ (已启动并运行)
- 足够的磁盘空间（用于BGE模型）

### 2. 安装依赖

```bash
# 安装RAG流水线依赖
pip install -r requirements_rag.txt

# 或者逐个安装核心依赖
pip install pymilvus>=2.3.0
pip install FlagEmbedding>=1.2.0
pip install langchain-core>=0.1.0
pip install langchain>=0.1.0
pip install openai>=1.0.0
pip install sse-starlette>=1.6.0
pip install httpx>=0.25.0
pip install fastapi>=0.104.0
```

### 3. 下载BGE模型

```bash
# 设置模型目录
export BGE_M3_PATH="/path/to/bge-m3"
export BGE_RERANKER_LARGE="/path/to/bge-reranker-large"

# 或在 .env 文件中配置
echo "BGE_M3_PATH=/path/to/bge-m3" >> .env
echo "BGE_RERANKER_LARGE=/path/to/bge-reranker-large" >> .env
```

---

## ⚙️ 配置说明

### 环境变量配置 (.env)

```bash
# === Milvus 配置 ===
MILVUS_URL=http://127.0.0.1:19530
CHUNKS_COLLECTION=kb_chunks_v1_v2  # 使用扩展版集合

# === OpenAI API 配置 ===
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_DEFAULT_MODEL=qwen-flash

# === BGE模型配置 ===
BGE_M3_PATH=/path/to/bge-m3
BGE_DEVICE=cpu  # 或 cuda
BGE_FP16=false  # 是否使用FP16精度

BGE_RERANKER_LARGE=/path/to/bge-reranker-large
BGE_RERANKER_DEVICE=cpu
BGE_RERANKER_FP16=false

# === RRF配置 ===
RRF_K=60  # RRF平滑参数
RRF_MAX_RESULTS=20  # RRF最大结果数

# === Reranker配置 ===
RERANK_MIN_TOP_K=3  # 断崖截断最小保留数
RERANK_MAX_TOP_K=10  # 断崖截断最大保留数
RERANK_GAP_THRESHOLD=0.15  # 断崖阈值

# === MCP联网搜索配置 ===
MCP_DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse
```

---

## 🚀 使用方法

### 方式1：直接使用流水线

```python
import asyncio
from processor.query_process.rag_pipeline_builder import run_rag_query

async def example():
    answer = await run_rag_query(
        query="宝宝挑食怎么办？",
        age_group="3-6岁",
        issue_type="健康饮食"
    )

    print(f"AI回答: {answer}")

asyncio.run(example())
```

### 方式2：测试完整流水线

```bash
# 运行完整测试
python scripts/test_rag_pipeline.py
```

### 方式3：使用流水线构建器

```python
import asyncio
from processor.query_process.rag_pipeline_builder import get_rag_pipeline
from processor.query_process.rag_state import QueryInput

async def example():
    pipeline = await get_rag_pipeline()

    query_input = QueryInput(
        query="孩子情绪失控怎么办？",
        age_group="通用",
        issue_type="情绪管理"
    )

    result = await pipeline(query_input)
    print(f"回答: {result.answer}")
    print(f"来源: {result.sources}")

asyncio.run(example())
```

---

## 📊 流水线架构

```
用户查询
    ↓
【入口节点】
    - 输入处理
    - 元数据提取
    ↓
【并行检索】(三路并行)
    ├─→ HybridVectorSearch (本地混合检索)
    ├─→ HyDeVectorSearch (假设性文档检索)
    └─→ WebMcpSearch (联网检索，可选)
    ↓
【RRF融合】
    - 多路结果合并
    - 去重排序
    ↓
【重排序】
    - BGE-Reranker精排
    - 断崖截断
    - 质量过滤
    ↓
【答案生成】
    - 基于精排上下文
    - 生成温暖专业的回答
    ↓
最终回答
```

---

## 🧪 测试验证

### 1. 测试依赖注入

```bash
python scripts/verify_dependency_injection.py
```

### 2. 测试扩展版Schema

```bash
python scripts/test_extended_schema.py
```

### 3. 测试RAG流水线

```bash
python scripts/test_rag_pipeline.py
```

---

## 📁 项目结构

```
processor/query_process/
├── rag_state.py              # RAG状态定义
├── rag_pipeline_builder.py    # RAG流水线构建器
└── nodes/
    ├── hybrid_vector_search_node.py    # 混合向量检索
    ├── hyde_vector_search_node.py      # HyDE检索
    ├── web_mcp_search_node.py           # 联网检索
    ├── rrf_merge_node.py                # RRF融合
    └── reranker_node.py                 # 重排序

utils/
├── client/
│   ├── storage_clients.py     # 存储客户端管理
│   └── ai_clients.py           # AI模型客户端管理
├── embedding_util.py          # 向量嵌入工具
├── milvus_util.py              # Milvus检索工具
└── query_prompt.py             # HyDE提示词模板

scripts/
├── verify_dependency_injection.py   # 依赖注入验证
├── test_extended_schema.py          # Schema测试
└── test_rag_pipeline.py             # RAG流水线测试
```

---

## ⚠️ 注意事项

### 1. 路径适配问题

老项目代码使用 `knowledge` 前缀，已适配为当前项目结构：
- `knowledge.processor.query_processor` → `processor.query_process`
- `knowledge.utils.client` → `utils.client`

### 2. 集合版本

- **旧集合**: `kb_chunks_v1` (旧Schema，不包含业务元数据)
- **新集合**: `kb_chunks_v1_v2` (扩展版Schema，包含 `content_type`, `author`, `age_group`, `issue_type`, `source_file`)

### 3. 模型依赖

- **BGE-M3**: 用于混合向量生成 (稠密+稀疏)
- **BGE-Reranker**: 用于重排序精排
- **LLM**: 用于HyDE假设文档生成和最终答案生成

---

## 🎯 下一步

### 完善功能

1. **元数据过滤**：在检索时应用 `age_group`, `issue_type` 过滤
2. **流式输出**：实现SSE流式推送，提升用户体验
3. **缓存优化**：对常见问题进行缓存，提升响应速度
4. **监控日志**：添加详细的性能监控和错误追踪

### 性能优化

1. **并行优化**：确保三路检索真正并行执行
2. **批量处理**：支持批量查询，提高吞吐量
3. **模型量化**：使用量化模型减少内存占用

---

## 📞 技术支持

如有问题，请检查：
1. Milvus服务是否正常运行
2. BGE模型路径是否正确配置
3. 环境变量是否正确设置
4. 依赖库版本是否兼容

祝使用愉快！🎉
