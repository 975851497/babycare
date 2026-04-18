"""
向量嵌入工具 - BGE-M3混合向量生成
"""

from typing import Dict, List
from FlagEmbedding import FlagModel


def generate_bge_m3_hybrid_vectors(model: FlagModel, embedding_documents: List[str]) -> Dict[str, List[List[float]]]:
    """
    使用BGE-M3生成混合向量（稠密+稀疏）

    Args:
        model: BGE-M3模型实例
        embedding_documents: 待嵌入的文档列表

    Returns:
        Dict[str, List[List[float]]]: 包含dense和sparse向量的字典
    """
    try:
        # 生成混合向量
        embeddings = model.encode_documents(embedding_documents)

        # 分离稠密和稀疏向量
        dense_vectors = []
        sparse_vectors = []

        for embedding in embeddings:
            if hasattr(embedding, 'dense'):
                dense_vectors.append(embedding.dense)
            else:
                # 兼容旧版本
                dense_vectors.append(embedding)

            if hasattr(embedding, 'sparse'):
                sparse_vectors.append(embedding.sparse)
            else:
                # 稀疏向量处理
                sparse_vectors.append({})

        return {
            'dense': dense_vectors,
            'sparse': sparse_vectors
        }

    except Exception as e:
        raise RuntimeError(f"BGE-M3向量生成失败: {str(e)}")


def generate_bge_m3_query_vector(model: FlagModel, query: str) -> Dict[str, List[float]]:
    """
    使用BGE-M3生成查询向量

    Args:
        model: BGE-M3模型实例
        query: 查询文本

    Returns:
        Dict[str, List[float]]: 包含dense和sparse向量的字典
    """
    try:
        # 生成查询向量
        embedding = model.encode_queries([query])

        # 分离稠密和稀疏向量
        dense_vector = embedding[0].dense if hasattr(embedding[0], 'dense') else embedding[0]
        sparse_vector = embedding[0].sparse if hasattr(embedding[0], 'sparse') else {}

        return {
            'dense': [dense_vector],
            'sparse': [sparse_vector]
        }

    except Exception as e:
        raise RuntimeError(f"BGE-M3查询向量生成失败: {str(e)}")


if __name__ == "__main__":
    # 测试向量生成
    print("🧪 测试BGE-M3向量生成")
    print("=" * 60)

    try:
        from utils.client.ai_clients import AIClients

        model = AIClients.get_bge_m3_client()

        # 测试文档嵌入
        docs = ["这是测试文档1", "这是测试文档2"]
        result = generate_bge_m3_hybrid_vectors(model, docs)

        print(f"✅ 文档嵌入成功")
        print(f"   Dense向量维度: {len(result['dense'][0])}")
        print(f"   Sparse向量非零元素: {len(result['sparse'][0])}")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
