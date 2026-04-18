"""向量库写入（MVP 模拟版本）"""

from typing import List
import uuid

# 模拟内存向量库（全局变量）
VECTOR_STORE = {}


def vector_upsert(state: dict) -> dict:
    embeddings: List[List[float]] = state.get("embeddings", [])
    chunks: List[str] = state.get("chunks", [])

    if not embeddings:
        return {
            "error": "embeddings 为空，无法存储",
            "status": "failed"
        }

    vector_ids = []

    for i, emb in enumerate(embeddings):
        vector_id = str(uuid.uuid4())

        # 存入“假向量库”
        VECTOR_STORE[vector_id] = {
            "embedding": emb,
            "text": chunks[i] if i < len(chunks) else ""
        }

        vector_ids.append(vector_id)

    return {"vector_ids": vector_ids}