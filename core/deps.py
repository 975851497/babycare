"""依赖注入：LLM、向量库、存储、任务队列等单例或工厂。"""

from core.settings import Settings, get_settings


def settings_dep() -> Settings:
    """FastAPI dependency-friendly settings getter."""

    return get_settings()
