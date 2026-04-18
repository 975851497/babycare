"""将文本 chunks 转换为向量嵌入（MVP 模拟版本）"""

from typing import List


def generate_embedding(state: dict) -> dict:
    chunks: List[str] = state.get("chunks", [])

    if not chunks:
        return {
            "error": "chunks 为空，无法生成 embeddings",
            "status": "failed"
        }

    embeddings = []

    for chunk in chunks:
        vector = []
        text = chunk.strip()

        # 防止空字符串
        if not text:
            text = " "

        # 生成固定 10 维向量
        for i in range(10):
            idx = i % len(text)
            val = (ord(text[idx]) + i) % 256  # 加一点扰动
            vector.append(val / 255.0)

        embeddings.append(vector)

    return {"embeddings": embeddings}