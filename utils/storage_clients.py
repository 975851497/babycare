"""存储客户端管理：Milvus、MinIO、MongoDB 单例管理。"""

import logging
from typing import Optional
from pymilvus import MilvusClient, connections

from core.settings import get_settings

logger = logging.getLogger(__name__)


class StorageClients:
    """存储客户端单例管理类"""

    _milvus_client: Optional[MilvusClient] = None

    @classmethod
    def get_milvus_client(cls) -> MilvusClient:
        """
        获取 Milvus 客户端单例

        Returns:
            MilvusClient: Milvus 客户端实例

        Raises:
            ConnectionError: 连接失败时抛出
        """
        if cls._milvus_client is None:
            try:
                settings = get_settings()
                milvus_url = settings.milvus_url

                logger.info(f"正在连接 Milvus: {milvus_url}")
                cls._milvus_client = MilvusClient(uri=milvus_url)
                logger.info("Milvus 客户端创建成功")

                # 测试连接
                if cls._milvus_client.list_collections() is not None:
                    logger.info("Milvus 连接测试成功")

            except Exception as e:
                logger.error(f"Milvus 客户端创建失败: {str(e)}")
                raise ConnectionError(f"Milvus 客户端创建失败: {str(e)}")

        return cls._milvus_client

    @classmethod
    def reset(cls):
        """重置所有客户端（主要用于测试）"""
        cls._milvus_client = None
        logger.info("已重置所有存储客户端")
