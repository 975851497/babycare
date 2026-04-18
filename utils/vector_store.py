"""向量库封装：集合管理、过滤检索、批量 upsert（Milvus 等）。"""

import math
from threading import Lock
from typing import Dict, List, Tuple


class VectorStore:
    """全局单例的内存向量数据库。

    使用字典存储向量数据，提供添加和检索功能。
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """实现单例模式。"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化向量存储。"""
        if self._initialized:
            return
        self._store: Dict[str, Dict[str, object]] = {}
        self._initialized = True

    def add_vector(self, id: str, text: str, embedding: List[float]) -> None:
        """存入向量。

        Args:
            id: 唯一标识符
            text: 文本内容
            embedding: 向量表示
        """
        self._store[id] = {
            "text": text,
            "embedding": embedding
        }

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Tuple[str, float]]:
        """使用余弦相似度计算，返回最相似的 Top K 文本列表。

        Args:
            query_embedding: 查询向量
            top_k: 返回最相似的结果数量

        Returns:
            List[Tuple[str, float]]: (文本, 相似度分数) 列表，按相似度降序排列
        """
        if not self._store:
            return []

        similarities = []
        for id, data in self._store.items():
            similarity = self._cosine_similarity(query_embedding, data["embedding"])
            similarities.append((data["text"], similarity))

        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度。

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            float: 余弦相似度分数
        """
        if len(vec1) != len(vec2):
            raise ValueError("向量维度不匹配")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def clear(self) -> None:
        """清空向量存储。"""
        self._store.clear()


# 全局单例实例
vector_store = VectorStore()
