"""
ImportMilvusNode 测试示例
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from processor.import_process.base import setup_logging
from processor.import_process.nodes.import_milvus import ImportMilvusNode


def create_test_data():
    """创建测试数据"""
    return {
        "chunks": [
            {
                "content": "宝宝挑食是很常见的问题，家长不要过于焦虑。",
                "title": "挑食问题",
                "parent_title": "育儿建议",
                "file_title": "餐桌冲突与挑食沟通话术",
                "item_name": "babycare",
                "dense_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "sparse_vector": {0: 0.5, 1: 0.8, 2: 0.3}
            },
            {
                "content": "孩子之间打架需要耐心调解，了解原因很重要。",
                "title": "手足冲突",
                "parent_title": "亲子关系",
                "file_title": "手足冲突调解沟通话术",
                "item_name": "babycare",
                "dense_vector": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1],
                "sparse_vector": {1: 0.6, 3: 0.9, 5: 0.4}
            },
            {
                "content": "家长情绪失控时，先深呼吸，等冷静后再沟通。",
                "title": "情绪管理",
                "parent_title": "家长成长",
                "file_title": "亲子冲突降温沟通话术",
                "item_name": "babycare",
                "dense_vector": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2],
                "sparse_vector": {2: 0.7, 4: 0.5, 6: 0.8}
            }
        ]
    }


def main():
    """主函数"""
    setup_logging()

    print("=" * 60)
    print("ImportMilvusNode 测试")
    print("=" * 60)

    # 1. 创建测试数据
    print("\n📝 创建测试数据...")
    state = create_test_data()
    print(f"✅ 测试数据已创建，包含 {len(state['chunks'])} 个 chunks")

    # 2. 创建节点实例
    print("\n🏗️  创建 ImportMilvusNode 实例...")
    node = ImportMilvusNode()
    print("✅ 节点实例创建成功")

    # 3. 执行导入
    print("\n🚀 开始执行导入...")
    try:
        result_state = node.process(state)

        # 4. 显示结果
        print("\n" + "=" * 60)
        print("✅ 导入成功！")
        print("=" * 60)

        for i, chunk in enumerate(result_state['chunks'], 1):
            chunk_id = chunk.get('chunk_id', 'N/A')
            content = chunk.get('content', '')[:50]
            print(f"[{i}] Chunk ID: {chunk_id}")
            print(f"    内容: {content}...")
            print()

        # 5. 保存结果
        output_path = Path(__file__).parent / "test_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_state, f, ensure_ascii=False, indent=4)
        print(f"📁 结果已保存至: {output_path}")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ 导入失败！")
        print("=" * 60)
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
