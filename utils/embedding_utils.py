"""嵌入模型调用、批处理与缓存。"""

import hashlib
from typing import List


def get_embedding(text: str) -> List[float]:
    """将文本转换为固定 10 维的浮点数向量（MVP 模拟版本）。

    使用基于字符编码的哈希映射算法，确保相同输入产生相同输出。
    这是一个简单的模拟实现，用于 MVP 快速上线。

    Args:
        text: 输入文本

    Returns:
        List[float]: 10 维浮点数向量
    """
    # 如果文本为空，返回零向量
    if not text:
        return [0.0] * 10

    # 使用 MD5 哈希确保相同输入产生相同输出
    hash_obj = hashlib.md5(text.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()

    # 将哈希值转换为 10 维向量
    embedding = []
    for i in range(10):
        # 每两个字符为一个 16 进制数
        start = i * 2
        end = start + 2
        hex_value = hash_hex[start:end]
        # 转换为 0-1 之间的浮点数
        float_value = int(hex_value, 16) / 255.0
        embedding.append(float_value)

    return embedding


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """批量获取文本向量。

    Args:
        texts: 输入文本列表

    Returns:
        List[List[float]]: 向量列表
    """
    return [get_embedding(text) for text in texts]
