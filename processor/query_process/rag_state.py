"""
查询状态定义 - 完整的RAG流程状态管理
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryGraphState(BaseModel):
    """
    查询流程的完整状态定义

    支持完整的RAG流水线：HybridVectorSearch -> HyDeVectorSearch -> WebMcpSearch -> RrfMerge -> Reranker -> AnswerOutput
    """

    # ===== 输入字段 =====
    original_query: Optional[str] = Field(None, description="用户原始查询")
    rewritten_query: Optional[str] = Field(None, description="LLM重写后的查询")
    item_names: List[str] = Field(default_factory=list, description="商品名列表 (育儿场景下为相关概念)")

    # ===== 向量检索结果 =====
    embedding_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="直接向量检索结果")
    hyde_embedding_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="HyDE假设文档检索结果")

    # ===== 融合结果 =====
    rrf_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="RRF融合后的检索结果")

    # ===== 联网检索结果 =====
    web_search_docs: Optional[List[Dict[str, Any]]] = Field(None, description="MCP联网检索结果")

    # ===== 重排序结果 =====
    reranked_docs: Optional[List[Dict[str, Any]]] = Field(None, description="经过BGE-Reranker精排后的文档")

    # ===== 最终回答 =====
    answer: Optional[str] = Field(None, description="生成的最终回答")

    # ===== 元数据字段 =====
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外的元数据信息")
    error: Optional[str] = Field(None, description="错误信息")
    status: str = "pending"  # pending -> searching -> reranking -> completed/failed


# 为了向后兼容，保留旧的 QueryState
class QueryState(BaseModel):
    """
    简化版查询状态 (用于兼容旧代码)
    """

    question: str = Field(..., description="用户输入的问题")
    retrieved_docs: List[str] = Field(default_factory=list, description="检索到的文档片段")
    final_answer: str = Field("", description="最终生成的回答")
    status: str = "pending"  # 当前状态
    error: Optional[str] = None  # 错误信息


class QueryInput(BaseModel):
    """查询输入模型"""
    query: str = Field(..., description="用户查询")
    age_group: Optional[str] = Field(None, description="年龄段过滤")
    issue_type: Optional[str] = Field(None, description="问题类型过滤")


class QueryOutput(BaseModel):
    """查询输出模型"""
    answer: str = Field(..., description="生成的回答")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="引用来源")
    confidence: float = Field(default=0.0, description="回答置信度")
