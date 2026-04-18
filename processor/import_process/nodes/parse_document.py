"""
文档解析节点 - 支持 MinerU
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Any


def _stream_mineru(cmd):
    """流式输出 MinerU 日志"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )

    logs = []
    for line in process.stdout:
        line = line.rstrip()
        logs.append(line)
        print(f"[MinerU] {line}")

    return_code = process.wait()
    return return_code, logs


def parse_document(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    文档解析节点

    Args:
        state: 包含 file_path 的状态字典

    Returns:
        state update dict，包含 raw_text 和 status
    """
    file_path = state.get("file_path")

    # 参数校验
    if not file_path:
        return {
            "status": "failed",
            "error": "file_path 为空",
            "current_step": "parse_document"
        }

    if not isinstance(file_path, str):
        return {
            "status": "failed",
            "error": "file_path 必须是字符串",
            "current_step": "parse_document"
        }

    if not os.path.exists(file_path):
        return {
            "status": "failed",
            "error": f"文件不存在: {file_path}",
            "current_step": "parse_document"
        }

    try:
        file_path_obj = Path(file_path)
        ext = file_path_obj.suffix.lower()

        # PDF 解析
        if ext == ".pdf":
            output_dir = file_path_obj.parent
            cmd = [
                "mineru",
                "-p",
                str(file_path_obj),
                "-o",
                str(output_dir),
                "--source",
                "local"
            ]

            print("\n===== 开始 MinerU 解析 =====\n")
            code, logs = _stream_mineru(cmd)

            if code != 0:
                return {
                    "status": "failed",
                    "error": "MinerU 解析失败",
                    "current_step": "parse_document"
                }

            file_name = file_path_obj.stem
            md_path = output_dir / file_name / "hybrid_auto" / f"{file_name}.md"

            if not md_path.exists():
                return {
                    "status": "failed",
                    "error": "未找到 md 文件",
                    "current_step": "parse_document"
                }

            raw_text = md_path.read_text(encoding="utf-8", errors="ignore")

        # TXT/MD 解析
        elif ext in [".txt", ".md"]:
            try:
                raw_text = file_path_obj.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raw_text = file_path_obj.read_text(encoding="gbk", errors="ignore")

        else:
            return {
                "status": "failed",
                "error": f"不支持的格式: {ext}",
                "current_step": "parse_document"
            }

        if not raw_text.strip():
            return {
                "status": "failed",
                "error": "文本为空",
                "current_step": "parse_document"
            }

        return {
            "raw_text": raw_text,
            "status": "success",
            "current_step": "parse_document"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "current_step": "parse_document"
        }
