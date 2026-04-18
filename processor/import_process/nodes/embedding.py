"""
向量生成节点 - 将文本 chunks 转换为向量嵌入
"""
from typing import Dict, Any, List

from utils.embedding_utils import get_embedding


def generate_embedding(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    向量生成节点

    Args:
        state: 包含 chunks 的状态字典

    Returns:
        state update dict，包含 embeddings 和 status
    """
    chunks: List[str] = state.get("chunks", [])

    # 参数校验
    if not chunks:
        return {
            "status": "failed",
            "error": "chunks 为空，无法生成 embeddings",
            "current_step": "generate_embedding"
        }

    try:
        # 使用统一的 embedding 工具函数
        embeddings = [get_embedding(chunk) for chunk in chunks]

        if not embeddings:
            return {
                "status": "failed",
                "error": "生成的 embeddings 为空",
                "current_step": "generate_embedding"
            }

        return {
            "embeddings": embeddings,
            "status": "success",
            "current_step": "generate_embedding"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": f"生成向量时发生异常: {str(e)}",
            "current_step": "generate_embedding"
        }
