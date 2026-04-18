"""查询状态：会话、用户问题、检索结果、引用片段、流式缓冲。"""

from typing import List, TypedDict, Optional


class QueryState(TypedDict, total=False):
    """查询流程的状态结构"""

    # 输入
    question: str  # 用户输入的问题

    # 中间数据
    retrieved_docs: List[str]  # 检索到的文档片段

    # 输出
    final_answer: str  # 最终生成的回答

    # 状态控制
    status: str  # 当前状态，例如 "searching", "answering", "completed", "failed"
    error: Optional[str]  # 错误信息
