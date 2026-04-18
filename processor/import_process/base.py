"""导入流程基础节点类。"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from core.settings import get_settings


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


class BaseNode(ABC):
    """导入流程基础节点类"""

    # 子类需要设置 name 属性
    name: str = "base_node"

    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.config = get_settings()

    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理状态的抽象方法

        Args:
            state: 输入状态字典

        Returns:
            Dict[str, Any]: 更新后的状态字典
        """
        pass

    def log_step(self, step: str, message: str):
        """
        记录处理步骤

        Args:
            step: 步骤名称
            message: 步骤信息
        """
        self.logger.info(f"[{self.name}] [{step}] {message}")

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        使节点可调用

        Args:
            state: 输入状态字典

        Returns:
            Dict[str, Any]: 更新后的状态字典
        """
        return self.process(state)
