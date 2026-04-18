"""全流程测试脚本：测试 Import 和 Query 流程的端到端功��。"""

import asyncio
import sys
import io
from pathlib import Path

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from processor.import_process.main_graph import run_import_pipeline
from processor.query_process.main_graph import run_query_pipeline


def print_section(title: str) -> None:
    """打印分节标题。

    Args:
        title: 标题文本
    """
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_import_flow() -> bool:
    """测试 Import 流程。

    Returns:
        是否成功
    """
    print_section("📥 第一步：测试 Import 流程")

    # 选择测试文件
    test_files = [
        project_root / "data/沟通话术/餐桌冲突与挑食沟通话术.md",
        project_root / "data/沟通话术/亲子冲突降温沟通话术.md",
        project_root / "data/沟通话术/手足冲突调解沟通话术.md"
    ]

    print(f"📁 测试文件数量: {len(test_files)}")

    success_count = 0
    for i, file_path in enumerate(test_files, 1):
        if not file_path.exists():
            print(f"❌ [{i}] 文件不存在: {file_path.name}")
            continue

        print(f"\n📄 [{i}] 导入文件: {file_path.name}")
        print("-" * 70)

        try:
            # 调用 Import 流程
            result = run_import_pipeline(str(file_path))

            # 检查结果
            status = result.get('status')
            if status == 'completed':
                success_count += 1
                print(f"✅ 导入成功")
                print(f"   - 文本长度: {len(result.get('raw_text', ''))}")
                print(f"   - 切分段数: {len(result.get('chunks', []))}")
                print(f"   - 向量数量: {len(result.get('embeddings', []))}")
                print(f"   - 向量ID数量: {len(result.get('vector_ids', []))}")
            else:
                print(f"❌ 导入失败: {status}")
                print(f"   错误信息: {result.get('error', '无')}")
                print(f"   当前步骤: {result.get('current_step', '无')}")

        except Exception as e:
            print(f"❌ 导入异常: {str(e)}")

    print(f"\n📊 Import 流程测试结果: {success_count}/{len(test_files)} 成功")
    return success_count > 0


async def test_query_flow() -> bool:
    """测试 Query 流程。

    Returns:
        是否成功
    """
    print_section("🔍 第二步：测试 Query 流程")

    # 定义测试问题
    test_questions = [
        "宝宝挑食怎么办？",
        "孩子之间打架如何处理？",
        "家长情绪失控怎么沟通？"
    ]

    print(f"❓ 测试问题数量: {len(test_questions)}")

    success_count = 0
    for i, question in enumerate(test_questions, 1):
        print(f"\n❓ [{i}] 用户问题: {question}")
        print("-" * 70)

        try:
            # 调用 Query 流程
            result = await run_query_pipeline(question)

            # 检查结果
            status = result.get('status')
            if status == 'completed':
                success_count += 1
                print(f"✅ 查询成功")
                print(f"   - 检索文档数: {len(result.get('retrieved_docs', []))}")

                # 打印最终回答
                final_answer = result.get('final_answer', '')
                if final_answer:
                    print(f"\n💡 AI 回答:")
                    # 限制回答长度，避免输出过长
                    preview = final_answer[:500]
                    print(preview)
                    if len(final_answer) > 500:
                        print("...\n(回答已截断，完整内容过长)")
                else:
                    print("⚠️  未生成回答")
            else:
                print(f"❌ 查询失败: {status}")
                print(f"   错误信息: {result.get('error', '无')}")

        except Exception as e:
            print(f"❌ 查询异常: {str(e)}")

    print(f"\n📊 Query 流程测试结果: {success_count}/{len(test_questions)} 成功")
    return success_count > 0


async def main():
    """主函数：全流程测试。"""
    print("\n" + "🚀" * 35)
    print("  Babycare 育儿知识库 - 全流程测试")
    print("🚀" * 35)

    # 第一步：测试 Import 流程
    import_success = test_import_flow()

    if not import_success:
        print("\n❌ Import 流程测试失败，跳过 Query 流程测试")
        return

    # 等待一下，确保数据已存储
    print("\n⏳ 等待数据存储完成...")
    await asyncio.sleep(1)

    # 第二步：测试 Query 流程
    query_success = await test_query_flow()

    # 最终总结
    print_section("📊 测试总结")

    if import_success and query_success:
        print("✅ 全流程测试通过！")
        print("   - Import 流程: 正常")
        print("   - Query 流程: 正常")
        print("\n🎉 系统运行正常，可以投入使用！")
    else:
        print("❌ 测试未完全通过")
        print(f"   - Import 流程: {'✅ 正常' if import_success else '❌ 异常'}")
        print(f"   - Query 流程: {'✅ 正常' if query_success else '❌ 异常'}")
        print("\n⚠️  请检查相关模块的配置和实现")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
