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
from processor.import_process.nodes.import_milvus import ImportMilvusNode
from processor.import_process.base import setup_logging
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

    # 设置日志
    setup_logging()

    # 选择测试文件
    test_files = [
        project_root / "data/沟通话术/餐桌冲突与挑食沟通话术.md",
        project_root / "data/沟通话术/亲子冲突降温沟通话术.md",
        project_root / "data/沟通话术/手足冲突调解沟通话术.md"
    ]

    print(f"📁 测试文件数量: {len(test_files)}")

    # 创建 Milvus 导入节点
    import_milvus_node = ImportMilvusNode()

    success_count = 0
    milvus_success_count = 0

    for i, file_path in enumerate(test_files, 1):
        if not file_path.exists():
            print(f"❌ [{i}] 文件不��在: {file_path.name}")
            continue

        print(f"\n📄 [{i}] 导入文件: {file_path.name}")
        print("-" * 70)

        try:
            # 第一步：调用 Import 流程（解析、切分、向量化）
            result = run_import_pipeline(str(file_path))

            # 检查结果
            status = result.get('status')
            if status == 'completed':
                success_count += 1
                print(f"✅ Import ���程成功")
                print(f"   - 文本长度: {len(result.get('raw_text', ''))}")
                print(f"   - 切分段数: {len(result.get('chunks', []))}")
                print(f"   - 向量数量: {len(result.get('embeddings', []))}")

                # 第二步：准备 Milvus 导入数据
                chunks = result.get('chunks', [])
                embeddings = result.get('embeddings', [])

                if not chunks or not embeddings:
                    print(f"⚠️  没有 chunks 或 embeddings，跳过 Milvus 导入")
                    continue

                # 构建 Milvus 导入格式
                milvus_data = []
                for chunk, embedding in zip(chunks, embeddings):
                    milvus_chunk = {
                        "content": chunk,
                        "title": file_path.stem,
                        "parent_title": "沟通话术",
                        "file_title": file_path.stem,
                        "item_name": "babycare",
                        "dense_vector": embedding,
                        # 生成简单的稀疏向量（MVP 版本）
                        "sparse_vector": {i: float(v) for i, v in enumerate(embedding) if v > 0.5}
                    }
                    milvus_data.append(milvus_chunk)

                # 第三步：调用 ImportMilvusNode 写入 Milvus
                print(f"📥 正在写入 Milvus ({len(milvus_data)} 个 chunks)...")
                state = {"chunks": milvus_data}

                try:
                    result_state = import_milvus_node.process(state)
                    milvus_success_count += 1

                    # 显示 Milvus 导入结果
                    print(f"✅ Milvus 写入成功")
                    imported_chunks = result_state.get('chunks', [])
                    print(f"   - 成功写入 {len(imported_chunks)} 个 chunks")

                    # 显示前 3 个 chunk_id
                    if imported_chunks:
                        chunk_ids = [chunk.get('chunk_id', 'N/A') for chunk in imported_chunks[:3]]
                        print(f"   - Chunk IDs: {chunk_ids}...")
                        if len(imported_chunks) > 3:
                            print(f"   - (还有 {len(imported_chunks) - 3} 个 chunks)")

                except Exception as milvus_error:
                    print(f"❌ Milvus 写入失败: {str(milvus_error)}")
                    # 继续处理下一个文件

            else:
                print(f"❌ 导入失败: {status}")
                print(f"   错误信息: {result.get('error', '无')}")
                print(f"   当前步骤: {result.get('current_step', '无')}")

        except Exception as e:
            print(f"❌ 导入异常: {str(e)}")

    print(f"\n📊 Import 流程测试结果: {success_count}/{len(test_files)} 成功")
    print(f"📊 Milvus 写入结果: {milvus_success_count}/{success_count} 成功")

    return success_count > 0 and milvus_success_count > 0


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
    print("  (包含 Milvus 真实写入)")
    print("🚀" * 35)

    # 第一步：测试 Import 流程（包含 Milvus 写入）
    import_success = test_import_flow()

    if not import_success:
        print("\n❌ Import 流程测试失败，跳过 Query 流程测试")
        return

    # 等待一下，确保数据已存储
    print("\n⏳ 等待 Milvus 数据索引完成...")
    await asyncio.sleep(2)

    # 第二步：测试 Query 流程
    query_success = await test_query_flow()

    # 最终总结
    print_section("📊 测试总结")

    if import_success and query_success:
        print("✅ 全流程测试通过！")
        print("   - Import 流程: 正常")
        print("   - Milvus 写入: 正常")
        print("   - Query 流程: 正常")
        print("\n🎉 系统运行正常，可以投入使用！")
        print("💡 数据已成功写入 Milvus，可以进行真实查询")
    else:
        print("❌ 测试未完全通过")
        print(f"   - Import 流程: {'✅ 正常' if import_success else '❌ 异常'}")
        print(f"   - Query 流程: {'✅ 正常' if query_success else '❌ 异常'}")
        print("\n⚠️  请检查相关模块的配置和实现")
        print("💡 特别检查：")
        print("   1. Milvus 服务是否启动")
        print("   2. .env 文件中 MILVUS_URL 配置是否正确")
        print("   3. 数据格式是否符合 ImportMilvusNode 要求")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
