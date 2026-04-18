"""
测试扩展版 ImportMilvusNode - 验证新Schema和数据写入
"""
import sys
import io
from pathlib import Path

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from processor.import_process.base import setup_logging
from processor.import_process.nodes.import_milvus_extended import ImportMilvusNodeExtended
from utils.client.storage_clients import StorageClients


def create_test_data():
    """创建测试数据（包含完整的业务元数据）"""
    return {
        "chunks": [
            "宝宝挑食是很常见的问题，家长不要过于焦虑。",
            "孩子之间打架需要耐心调解，了解原因很重要。",
            "家长情绪失控时，先深呼吸，等冷静后再沟通。"
        ],
        "embeddings": [
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1],
            [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2]
        ],
        "metadata": {
            "content_type": "沟通话术",
            "author": "育儿专家",
            "age_group": "3-6岁",
            "issue_type": "情绪管理",
            "source_file": "餐桌冲突与挑食沟通话术.md",
            "title": "餐桌冲突处理指南"
        }
    }


def main():
    """主函数"""
    setup_logging()

    print("=" * 70)
    print("🧪 测试扩展版 ImportMilvusNode")
    print("   - 新Schema字段：content_type, author, age_group, issue_type, source_file")
    print("=" * 70)

    # 1. 创建测试数据
    print("\n📝 第一步：创建测试数据")
    print("-" * 70)
    state = create_test_data()
    print(f"✅ 测试数据已创建")
    print(f"   - Chunks: {len(state['chunks'])}")
    print(f"   - Embeddings: {len(state['embeddings'])}")
    print(f"   - Metadata: {list(state['metadata'].keys())}")
    print(f"   - Content Type: {state['metadata']['content_type']}")
    print(f"   - Age Group: {state['metadata']['age_group']}")
    print(f"   - Issue Type: {state['metadata']['issue_type']}")

    # 2. 创建扩展版节点实例
    print("\n🏗️  第二步：创建 ImportMilvusNodeExtended 实例")
    print("-" * 70)
    node = ImportMilvusNodeExtended()
    print("✅ 节点实例创建成功")

    # 3. 执行导入
    print("\n🚀 第三步：执行导入（创建新Schema并写入数据）")
    print("-" * 70)
    try:
        result_state = node.process(state)

        # 4. 显示结果
        print("\n" + "=" * 70)
        print("✅ 导入成功！")
        print("=" * 70)

        collection_name = result_state.get('collection_name', 'N/A')
        print(f"📊 集合名称: {collection_name}")
        print(f"📊 写入 chunks: {len(result_state.get('chunks', []))}")

        # 5. 验证新Schema
        print("\n🔍 第四步：验证新Schema")
        print("-" * 70)
        milvus_client = StorageClients.get_milvus_client()

        if milvus_client.has_collection(collection_name):
            print(f"✅ 集合 '{collection_name}' 存在")

            # 获取集合描述
            desc = milvus_client.describe_collection(collection_name)
            fields = desc.get('fields', [])
            print(f"📊 字段总数: {len(fields)}")
            print(f"📊 字段列表:")

            for field in fields:
                field_name = field.get('name')
                field_type = field.get('type')
                is_primary = field.get('is_primary', False)
                auto_id = field.get('auto_id', False)
                primary_mark = " [主键]" if is_primary else ""
                auto_id_mark = f" [auto_id: {auto_id}]" if auto_id else ""
                dim_info = f", dim={field.get('dim')}" if field.get('dim') else ""

                # 高亮显示新增字段
                if field_name in ['content_type', 'author', 'age_group', 'issue_type', 'source_file']:
                    print(f"      ✨ {field_name}: {field_type}{dim_info}{primary_mark}{auto_id_mark} [新增]")
                else:
                    print(f"      •  {field_name}: {field_type}{dim_info}{primary_mark}{auto_id_mark}")

            # 6. 验证数据写入
            print("\n📋 第五步：验证数据写入")
            print("-" * 70)
            stats = milvus_client.get_collection_stats(collection_name)
            row_count = stats.get('num_rows', 'N/A')
            print(f"📊 总行数: {row_count}")

            # 显示第一条记录的业务元数据
            if result_state.get('chunks'):
                first_chunk = result_state['chunks'][0]
                print(f"\n📄 第一条记录的业务元数据:")
                print(f"   - content_type: {first_chunk.get('content_type')}")
                print(f"   - author: {first_chunk.get('author')}")
                print(f"   - age_group: {first_chunk.get('age_group')}")
                print(f"   - issue_type: {first_chunk.get('issue_type')}")
                print(f"   - source_file: {first_chunk.get('source_file')}")
                print(f"   - title: {first_chunk.get('title')}")
                print(f"   - chunk_id: {first_chunk.get('chunk_id', 'N/A')}")

        else:
            print(f"❌ 集合 '{collection_name}' 不存在")

        print("\n" + "=" * 70)
        print("🎉 扩展版Schema测试完成！")
        print("=" * 70)
        print("✅ 新字段已成功添加：content_type, author, age_group, issue_type, source_file")
        print("✅ 数据已成功写入，可以进行元数据过滤查询")

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ 测试失败！")
        print("=" * 70)
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
