"""
导入流程的统一 State 定义 - LangGraph 兼容版本
"""
from typing import List, TypedDict, Optional, Annotated
from operator import add


class ImportState(TypedDict, total=False):
    """导入流程的状态结构"""

    # 输入
    file_path: str

    # 中间数据
    raw_text: str
    chunks: List[str]
    embeddings: List[List[float]]
    vector_ids: List[str]

    # 状态控制
    status: str  # "pending" | "completed" | "failed" | "success"
    error: Optional[str]

    # 元数据
    current_step: str  # 当前执行到哪个步骤
