"""
向量生成节点 - 将文本 chunks 转换为向量嵌入
"""
from typing import Dict, Any, List


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

    embeddings = []

    # MVP: 简单的模拟向量生成
    for chunk in chunks:
        vector = []
        text = chunk.strip()

        # 防止空字符串
        if not text:
            text = " "

        # 生成固定 10 维向量（MVP 版本）
        for i in range(10):
            idx = i % len(text)
            val = (ord(text[idx]) + i) % 256
            vector.append(val / 255.0)

        embeddings.append(vector)

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
