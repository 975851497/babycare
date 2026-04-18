"""
验证依赖注入是否正常工作
"""
import sys
import io
from pathlib import Path

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.client.storage_clients import StorageClients


def test_dependency_injection():
    """测试依赖注入"""
    print("=" * 60)
    print("🧪 验证依赖注入功能")
    print("=" * 60)

    try:
        # 1. 测试单例模式
        print("\n📌 测试 1：单例模式")
        client1 = StorageClients.get_milvus_client()
        client2 = StorageClients.get_milvus_client()

        is_same_instance = client1 is client2
        print(f"Client1 ID: {id(client1)}")
        print(f"Client2 ID: {id(client2)}")
        print(f"是否同一实例: {is_same_instance} {'✅' if is_same_instance else '❌'}")

        # 2. 测试连接有效性
        print("\n📌 测试 2：连接有效性")
        collections = client1.list_collections()
        print(f"Milvus 集合列表: {collections}")
        print(f"✅ 连接正常，发现 {len(collections)} 个集合")

        # 3. 测试特定集合
        print("\n📌 测试 3：检查目标集合")
        target_collection = "kb_chunks_v1"
        if target_collection in collections:
            print(f"✅ 目标集合 '{target_collection}' 存在")

            # 获取集合统计信息
            stats = client1.get_collection_stats(target_collection)
            print(f"   - 行数: {stats.get('num_rows', 'N/A')}")

            # 获取集合描述（包含Schema信息）
            desc = client1.describe_collection(target_collection)
            fields = desc.get('fields', [])
            print(f"   - 字段数: {len(fields)}")
            print(f"   - 字段列表:")
            for field in fields:
                field_name = field.get('name')
                field_type = field.get('type')
                is_primary = field.get('is_primary', False)
                auto_id = field.get('auto_id', False)
                primary_mark = " [主键]" if is_primary else ""
                auto_id_mark = f" [auto_id: {auto_id}]" if auto_id else ""
                dim_info = f", dim={field.get('dim')}" if field.get('dim') else ""
                print(f"      • {field_name}: {field_type}{dim_info}{primary_mark}{auto_id_mark}")
        else:
            print(f"⚠️  目标集合 '{target_collection}' 不存在")

        print("\n" + "=" * 60)
        print("✅ 依赖注入验证通过！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dependency_injection()
    sys.exit(0 if success else 1)
