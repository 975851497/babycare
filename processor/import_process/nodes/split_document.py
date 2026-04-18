"""
文本切分节点 - 将文档切分为可处理的 chunks
"""
from typing import Dict, Any, List


def split_document(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    文本切分节点

    Args:
        state: 包含 raw_text 的状态字典

    Returns:
        state update dict，包含 chunks 和 status
    """
    raw_text: str = state.get("raw_text", "")

    # 参数校验
    if not raw_text or not raw_text.strip():
        return {
            "status": "failed",
            "error": "raw_text 为空，无法切分",
            "current_step": "split_document"
        }

    chunks = []

    # 按换行分段
    paragraphs = raw_text.split("\n")

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 短段落直接使用
        if len(para) <= 500:
            chunks.append(para)
        else:
            # 长段落按长度切分
            start = 0
            while start < len(para):
                end = start + 400
                chunk = para[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end

    if not chunks:
        return {
            "status": "failed",
            "error": "切分后没有有效内容",
            "current_step": "split_document"
        }

    return {
        "chunks": chunks,
        "status": "success",
        "current_step": "split_document"
    }
