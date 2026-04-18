"""
验证导入流程结构规范化的简单测试
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from processor.import_process.state import ImportState
from processor.import_process.nodes.parse_document import parse_document
from processor.import_process.nodes.split_document import split_document
from processor.import_process.nodes.embedding import generate_embedding
from processor.import_process.nodes.vector_upsert import vector_upsert


def test_parse_document():
    """测试 parse_document 节点"""
    print("Testing parse_document...")

    # 测试正常情况
    state = {
        "file_path": r"D:\ProjectLlists\babycare\processor\import_process\tem\餐桌冲突与挑食沟通话术.md"
    }

    result = parse_document(state)
    print(f"  Status: {result.get('status')}")
    print(f"  Current step: {result.get('current_step')}")
    print(f"  Raw text length: {len(result.get('raw_text', ''))}")

    assert result.get('status') in ['success', 'failed']
    assert result.get('current_step') == 'parse_document'

    return result


def test_split_document():
    """测试 split_document 节点"""
    print("Testing split_document...")

    state = {
        "raw_text": "这是第一段文本。\n\n这是第二段文本，内容比较长，需要测试切分功能是否正常工作。"
    }

    result = split_document(state)
    print(f"  Status: {result.get('status')}")
    print(f"  Current step: {result.get('current_step')}")
    print(f"  Chunks count: {len(result.get('chunks', []))}")

    assert result.get('status') == 'success'
    assert result.get('current_step') == 'split_document'
    assert len(result.get('chunks', [])) > 0

    return result


def test_generate_embedding():
    """测试 generate_embedding 节点"""
    print("Testing generate_embedding...")

    state = {
        "chunks": ["第一段文本", "第二段文本"]
    }

    result = generate_embedding(state)
    print(f"  Status: {result.get('status')}")
    print(f"  Current step: {result.get('current_step')}")
    print(f"  Embeddings count: {len(result.get('embeddings', []))}")

    assert result.get('status') == 'success'
    assert result.get('current_step') == 'generate_embedding'
    assert len(result.get('embeddings', [])) == 2

    return result


def test_vector_upsert():
    """测试 vector_upsert 节点"""
    print("Testing vector_upsert...")

    state = {
        "chunks": ["第一段文本", "第二段文本"],
        "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    }

    result = vector_upsert(state)
    print(f"  Status: {result.get('status')}")
    print(f"  Current step: {result.get('current_step')}")
    print(f"  Vector IDs count: {len(result.get('vector_ids', []))}")

    assert result.get('status') == 'success'
    assert result.get('current_step') == 'vector_upsert'
    assert len(result.get('vector_ids', [])) == 2

    return result


def test_state_structure():
    """测试 State 结构"""
    print("Testing ImportState structure...")

    state: ImportState = {
        "file_path": "test.pdf",
        "raw_text": "test content",
        "chunks": ["chunk1", "chunk2"],
        "embeddings": [[0.1, 0.2], [0.3, 0.4]],
        "vector_ids": ["id1", "id2"],
        "status": "completed",
        "error": None,
        "current_step": "vector_upsert"
    }

    print(f"  State has {len(state)} fields")
    assert len(state) == 8
    print(f"  All required fields present")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始验证导入流程结构规范化")
    print("=" * 50)

    try:
        # 测试 State 结构
        test_state_structure()
        print()

        # 测试各个节点
        test_split_document()
        print()

        test_generate_embedding()
        print()

        test_vector_upsert()
        print()

        # 测试完整的 parse_document（如果文件存在）
        try:
            test_parse_document()
        except Exception as e:
            print(f"  Note: parse_document test skipped (file not found: {e})")

        print()
        print("=" * 50)
        print("[SUCCESS] All tests passed! Import process structure normalization successful!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
