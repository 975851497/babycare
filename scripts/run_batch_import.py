"""批量导入脚本：遍历 data 目录下的所有文件并执行导入流程。"""

import os
import sys
from pathlib import Path
from typing import List, Dict

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from processor.import_process.main_graph import run_import_pipeline


# 支持的文件类型
SUPPORTED_EXTENSIONS = {'.md', '.txt', '.pdf'}


def collect_files(data_dir: Path) -> List[Path]:
    """递归收集 data 目录下的所有支持格式的文件。

    Args:
        data_dir: data 目录路径

    Returns:
        文件路径列表
    """
    files = []

    if not data_dir.exists():
        print(f"❌ 数据目录不存在: {data_dir}")
        return files

    for file_path in data_dir.rglob('*'):
        # 只处理文件（跳过目录）
        if not file_path.is_file():
            continue

        # 检查文件扩展名
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file_path)

    return sorted(files)


def process_file(file_path: Path) -> Dict[str, object]:
    """处理单个文件。

    Args:
        file_path: 文件路径

    Returns:
        处理结果字典
    """
    try:
        # 调用导���流程
        result = run_import_pipeline(str(file_path))

        # 提取关键信息
        status = result.get('status', 'unknown')
        error = result.get('error', '')
        current_step = result.get('current_step', '')

        return {
            'file': file_path,
            'status': status,
            'error': error,
            'current_step': current_step,
            'success': status == 'completed'
        }

    except Exception as e:
        return {
            'file': file_path,
            'status': 'failed',
            'error': str(e),
            'current_step': '',
            'success': False
        }


def print_summary(results: List[Dict[str, object]]) -> None:
    """打印处理结果摘要。

    Args:
        results: 处理结果列表
    """
    total = len(results)
    success = sum(1 for r in results if r['success'])
    failed = total - success

    print("\n" + "="*60)
    print("📊 批量导入完成！")
    print("="*60)
    print(f"总计: {total} 个文件")
    print(f"✅ 成功: {success} 个")
    print(f"❌ 失败: {failed} 个")
    print("="*60)

    # 打印失败的文件
    if failed > 0:
        print("\n❌ 失败文件列表:")
        for result in results:
            if not result['success']:
                print(f"  - {result['file']}")
                print(f"    错误: {result['error']}")
                print()


def main():
    """主函数：批量导入流程。"""
    # 获取 data 目录路径
    data_dir = project_root / "data"

    print("="*60)
    print("🚀 开始批量导入育儿知识库")
    print("="*60)
    print(f"📁 数据目录: {data_dir}")
    print(f"📄 支持格式: {', '.join(SUPPORTED_EXTENSIONS)}")
    print("="*60)

    # 收集文件
    print("\n🔍 扫描文件...")
    files = collect_files(data_dir)

    if not files:
        print("❌ 未找到任何文件，请检查 data 目录")
        return

    print(f"✅ 找到 {len(files)} 个文件")
    print()

    # 批量处理
    results = []
    for i, file_path in enumerate(files, 1):
        # 打印当前处理进度
        relative_path = file_path.relative_to(data_dir)
        print(f"[{i}/{len(files)}] 处理: {relative_path}", end=" ")

        # 处理文件
        result = process_file(file_path)
        results.append(result)

        # 打印处理结果
        if result['success']:
            print("✅ 成功")
        else:
            print(f"❌ 失败")
            print(f"    错误: {result['error']}")

    # 打印摘要
    print_summary(results)


if __name__ == "__main__":
    main()
