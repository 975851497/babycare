"""文本切分（MVP 简单版本）"""

from typing import List


def chunk_content(state: dict) -> dict:
    raw_text: str = state.get("raw_text", "")

    if not raw_text or not raw_text.strip():
        return {
            "error": "raw_text 为空，无法切分",
            "status": "failed"
        }

    chunks = []

    # 按换行分段
    paragraphs = raw_text.split("\n")

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 如果不长，直接用
        if len(para) <= 500:
            chunks.append(para)
        else:
            # 简单按长度切
            start = 0
            while start < len(para):
                end = start + 400
                chunk = para[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end

    return {"chunks": chunks}