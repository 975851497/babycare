"""快速调试脚本：验证 embedding 和向量存储是否正常。"""

import sys
import io
from pathlib import Path

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.embedding_utils import get_embedding
from utils.vector_store import vector_store


def test_embedding_consistency():
    """测试 embedding 的一致性。"""
    print("="*60)
    print("🧪 测试 1: Embedding 一致性")
    print("="*60)

    test_text = "宝宝挑食怎么办？"

    # 生成两次 embedding，看是否一致
    emb1 = get_embedding(test_text)
    emb2 = get_embedding(test_text)

    print(f"📝 测试文本: {test_text}")
    print(f"📊 向量维度: {len(emb1)}")
    print(f"✅ 一致性: {'通过' if emb1 == emb2 else '失败'}")
    print(f"📌 向量前5位: {emb1[:5]}")

    return emb1 == emb2


def test_vector_storage():
    """测试向量存储和检索。"""
    print("\n" + "="*60)
    print("🧪 测试 2: 向量存储和检索")
    print("="*60)

    # 清空向量库
    vector_store.clear()

    # 添加测试数据
    test_data = [
        ("doc1", "宝宝挑食是很常见的问题，家长不要过于焦虑"),
        ("doc2", "孩子之间打架需要耐心调解，了解���因很重要"),
        ("doc3", "家长情绪失控时，先深呼吸，等冷静后再沟通")
    ]

    print("📥 添加测试数据...")
    for doc_id, text in test_data:
        embedding = get_embedding(text)
        vector_store.add_vector(doc_id, text, embedding)
        print(f"  ✅ 添加: {doc_id}")

    # 测试检索
    print("\n🔍 测试检索...")
    query = "宝宝挑食怎么办？"
    query_embedding = get_embedding(query)
    results = vector_store.search(query_embedding, top_k=3)

    print(f"❓ 查询: {query}")
    print(f"📊 召回结果数: {len(results)}")

    if results:
        print("\n✅ 检索成功！召回的文档：")
        for i, (text, score) in enumerate(results, 1):
            print(f"  [{i}] 相似度: {score:.4f}")
            print(f"      内容: {text[:50]}...")
    else:
        print("❌ 检索失败！没有召回任何文档")

    return len(results) > 0


def main():
    """主函数。"""
    print("\n🚀 向量系统调试工具\n")

    test1_pass = test_embedding_consistency()
    test2_pass = test_vector_storage()

    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"Embedding 一致性: {'✅ 通过' if test1_pass else '❌ 失败'}")
    print(f"向量存储检索: {'✅ 通过' if test2_pass else '❌ 失败'}")

    if test1_pass and test2_pass:
        print("\n🎉 所有测试通过！向量系统工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关模块。")


if __name__ == "__main__":
    main()
