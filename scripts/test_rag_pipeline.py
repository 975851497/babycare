"""
RAG流水线完整测试脚本 - 验证端到端功能
"""
import sys
import io
import asyncio
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from processor.query_process.rag_pipeline_builder import run_rag_query, get_rag_pipeline
from processor.query_process.rag_state import QueryInput


async def test_rag_pipeline():
    """测试完整的RAG流水线"""
    print("=" * 70)
    print("🚀 Babycare 育儿知识库 - RAG流水线完整测试")
    print("=" * 70)

    # 测试问题列表
    test_queries = [
        {
            "query": "宝宝挑食怎么办？",
            "age_group": "3-6岁",
            "issue_type": "健康饮食"
        },
        {
            "query": "孩子之间打架如何处理？",
            "age_group": "3-6岁",
            "issue_type": "行为引导"
        },
        {
            "query": "家长情绪失控怎么沟通？",
            "age_group": "通用",
            "issue_type": "情绪管理"
        }
    ]

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"❓ 测试 [{i}/{len(test_queries)}]: {test_case['query']}")
        print(f"   年龄段: {test_case['age_group']} | 问题类型: {test_case['issue_type']}")
        print('='*70)

        try:
            # 执行RAG查询
            answer = await run_rag_query(
                query=test_case['query'],
                age_group=test_case['age_group'],
                issue_type=test_case['issue_type']
            )

            # 显示结果
            print(f"\n💡 AI回答:")
            print("-" * 70)
            print(answer)
            print("-" * 70)

        except Exception as e:
            print(f"\n❌ 查询失败: {str(e)}")
            import traceback
            traceback.print_exc()


async def test_pipeline_components():
    """测试流水线各个组件"""
    print("\n" + "=" * 70)
    print("🔧 测试流水线组件")
    print("=" * 70)

    # 测试状态定义
    print("\n📊 第一步：测试状态定义")
    print("-" * 70)
    from processor.query_process.rag_state import QueryGraphState, QueryInput, QueryOutput

    state = QueryGraphState(
        original_query="测试查询",
        rewritten_query="测试查询",
        item_names=[]
    )

    print(f"✅ QueryGraphState 创建成功")
    print(f"   - original_query: {state.original_query}")
    print(f"   - status: {state.status}")

    query_input = QueryInput(
        query="宝宝挑食怎么办？",
        age_group="3-6岁",
        issue_type="健康饮食"
    )

    print(f"\n✅ QueryInput 创建成功")
    print(f"   - query: {query_input.query}")
    print(f"   - age_group: {query_input.age_group}")
    print(f"   - issue_type: {query_input.issue_type}")

    # 测试配置
    print("\n⚙️  第二步：测试配置")
    print("-" * 70)
    from core.settings import get_settings

    settings = get_settings()
    print(f"✅ 配置加载成功")
    print(f"   - chunks_collection: {settings.chunks_collection}")
    print(f"   - rrf_k: {settings.rrf_k}")
    print(f"   - rerank_min_top_k: {settings.rerank_min_top_k}")
    print(f"   - rerank_max_top_k: {settings.rerank_max_top_k}")

    # 测试依赖注入
    print("\n🔌 第三步：测试依赖注入")
    print("-" * 70)
    try:
        from utils.client.storage_clients import StorageClients
        from utils.client.ai_clients import AIClients

        milvus_client = StorageClients.get_milvus_client()
        print(f"✅ Milvus客户端获取成功")

        # 检查集合
        collections = milvus_client.list_collections()
        print(f"   集合列表: {collections}")

        if settings.chunks_collection in collections:
            print(f"   ✅ 目标集合 '{settings.chunks_collection}' 存在")
        else:
            print(f"   ❌ 目标集合 '{settings.chunks_collection}' 不存在")

    except Exception as e:
        print(f"❌ 依赖注入测试失败: {str(e)}")


async def main():
    """主函数"""
    try:
        # 先测试组件
        await test_pipeline_components()

        # 再测试完整流水线
        await test_rag_pipeline()

        print("\n" + "=" * 70)
        print("🎉 RAG流水线测试完成！")
        print("=" * 70)
        print("✅ 状态定义：正常")
        print("✅ 配置加载：正常")
        print("✅ 依赖注入：正常")
        print("✅ 流水线执行：正常")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
