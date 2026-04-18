"""
向量存储节点 - 将向量写入向量库
"""
from typing import Dict, Any, List
import uuid

from utils.vector_store import vector_store


def vector_upsert(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    向量存储节点

    Args:
        state: 包含 embeddings 和 chunks 的状态字典

    Returns:
        state update dict，包含 vector_ids 和 status
    """
    embeddings: List[List[float]] = state.get("embeddings", [])
    chunks: List[str] = state.get("chunks", [])

    # 参数校验
    if not embeddings:
        return {
            "status": "failed",
            "error": "embeddings 为空，无法存储",
            "current_step": "vector_upsert"
        }

    vector_ids = []

    # 存储到全局向量库单例
    for i, emb in enumerate(embeddings):
        vector_id = str(uuid.uuid4())

        # 获取对应的文本
        text = chunks[i] if i < len(chunks) else ""

        # 存入全局向量库
        vector_store.add_vector(vector_id, text, emb)

        vector_ids.append(vector_id)

    if not vector_ids:
        return {
            "status": "failed",
            "error": "存储失败，vector_ids 为空",
            "current_step": "vector_upsert"
        }

    return {
        "vector_ids": vector_ids,
        "status": "success",
        "current_step": "vector_upsert"
    }
