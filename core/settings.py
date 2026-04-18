"""Centralized settings loader for the babycare project."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Service ports
    import_service_port: int = Field(8000, alias="IMPORT_SERVICE_PORT")
    query_service_port: int = Field(8001, alias="QUERY_SERVICE_PORT")

    # OpenAI / DashScope compatible
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_api_base: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", alias="OPENAI_API_BASE")
    llm_default_model: str = Field("qwen-flash", alias="LLM_DEFAULT_MODEL")
    llm_default_temperature: float = Field(0.1, alias="LLM_DEFAULT_TEMPERATURE")

    # Model routing
    vl_model: str = Field("qwen3-vl-flash", alias="VL_MODEL")
    item_model: str = Field("qwen-flash", alias="ITEM_MODEL")
    kg_model: str = Field("qwen-flash", alias="KG_MODEL")

    # Embedding / reranker
    bge_m3_path: str = Field("", alias="BGE_M3_PATH")
    bge_device: str = Field("cpu", alias="BGE_DEVICE")
    bge_fp16: bool = Field(False, alias="BGE_FP16")
    bge_reranker_large: str = Field("", alias="BGE_RERANKER_LARGE")
    bge_reranker_device: str = Field("cpu", alias="BGE_RERANKER_DEVICE")
    bge_reranker_fp16: bool = Field(False, alias="BGE_RERANKER_FP16")
    item_name_diag: int = Field(0, alias="ITEM_NAME_DIAG")

    # Generic embedding
    embedding_dim: int = Field(1536, alias="EMBEDDING_DIM")
    embedding_model: str = Field("text-embedding-v4", alias="EMBEDDING_MODEL")

    # Milvus
    milvus_url: str = Field("http://127.0.0.1:19530", alias="MILVUS_URL")
    chunks_collection: str = Field("kb_chunks_v1_v2", alias="CHUNKS_COLLECTION")  # 更新为扩展版集合
    item_name_collection: str = Field("kb_item_names_v1", alias="ITEM_NAME_COLLECTION")
    milvus_metric_type: str = Field("COSINE", alias="MILVUS_METRIC_TYPE")
    milvus_min_cosine_score: float = Field(0.75, alias="MILVUS_MIN_COSINE_SCORE")

    # RRF (Reciprocal Rank Fusion) 配置
    rrf_k: int = Field(60, alias="RRF_K")  # RRF 平滑参数 (默认60)
    rrf_max_results: int = Field(20, alias="RRF_MAX_RESULTS")  # RRF 最大结果数

    # Reranker 配置
    rerank_min_top_k: int = Field(3, alias="RERANK_MIN_TOP_K")  # 最少保留文档数 (断崖截断兜底)
    rerank_max_top_k: int = Field(10, alias="RERANK_MAX_TOP_K")  # 最多保留文档数
    rerank_gap_threshold: float = Field(0.15, alias="RERANK_GAP_THRESHOLD")  # 断崖阈值 (默认0.15)

    # MongoDB
    mongo_url: str = Field("mongodb://127.0.0.1:27017", alias="MONGO_URL")
    mongo_db_name: str = Field("kb001", alias="MONGO_DB_NAME")

    # MinIO
    minio_endpoint: str = Field("127.0.0.1:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field("minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field("knowledge-base-v1", alias="MINIO_BUCKET_NAME")

    # MCP services
    mcp_dashscope_base_url: str = Field(
        "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse", alias="MCP_DASHSCOPE_BASE_URL"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return singleton settings instance."""

    return Settings()
