"""文档解析（支持 MinerU）"""

import os
import subprocess
from pathlib import Path


def stream_mineru(cmd):
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


def parse_document(state: dict) -> dict:
    """
    输入:
        state["file_path"]

    输出:
        raw_text / status / error
    """
    file_path = state.get("file_path")

    if not file_path:
        return {"error": "file_path 为空", "status": "failed"}

    if not isinstance(file_path, str):
        return {"error": "file_path 必须是字符串", "status": "failed"}

    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}", "status": "failed"}

    try:
        file_path_obj = Path(file_path)
        ext = file_path_obj.suffix.lower()

        # ===== PDF =====
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

            code, logs = stream_mineru(cmd)

            if code != 0:
                return {
                    "status": "failed",
                    "error": "MinerU 解析失败"
                }

            file_name = file_path_obj.stem
            md_path = output_dir / file_name / "hybrid_auto" / f"{file_name}.md"

            if not md_path.exists():
                return {"status": "failed", "error": "未找到 md 文件"}

            raw_text = md_path.read_text(encoding="utf-8", errors="ignore")

        # ===== txt / md =====
        elif ext in [".txt", ".md"]:
            try:
                raw_text = file_path_obj.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raw_text = file_path_obj.read_text(encoding="gbk", errors="ignore")

        else:
            return {"status": "failed", "error": f"不支持的格式: {ext}"}

        if not raw_text.strip():
            return {"status": "failed", "error": "文本为空"}

        return {
            "raw_text": raw_text,
            "status": "success"
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}