"""向量检索 + 可选关键词；返回带元数据的 chunk 列表。"""

from typing import List

from processor.query_process.state import QueryState
from utils.embedding_utils import get_embedding
from utils.vector_store import vector_store


async def knowledge_search(state: QueryState) -> QueryState:
    """知识搜索节点：检索相关文档片段。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    try:
        # 获取用户问题
        question = state.get("question", "")

        if not question:
            return {
                **state,
                "status": "failed",
                "error": "问题为空，无法检索"
            }

        # 将问题转为向量
        query_embedding = get_embedding(question)

        # 搜索 Top 3 结果
        search_results = vector_store.search(query_embedding, top_k=3)

        # 提取文��内容
        retrieved_docs = [text for text, score in search_results]

        return {
            **state,
            "retrieved_docs": retrieved_docs,
            "status": "answering"
        }

    except Exception as e:
        return {
            **state,
            "status": "failed",
            "error": f"知识检索失败: {str(e)}"
        }
