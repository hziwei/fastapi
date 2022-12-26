import abc
from typing import Callable

from test_fastapi.utils.config import Config


class BaseDriver(abc.ABC):

    def __init__(self, config: Config):
        self.config: Config = config
        pass

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """驱动器名称"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def logger(self):
        """驱动专属 logger 日志记录器"""
        raise NotImplementedError

    @property
    def asgi(self):
        """`FastAPI APP` 对象"""
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        """启动驱动框架"""
        raise NotImplementedError

    @abc.abstractmethod
    def on_startup(self, func: Callable) -> Callable:
        """注册一个在驱动器启动时执行的函数"""
        raise NotImplementedError

    @abc.abstractmethod
    def on_shutdown(self, func: Callable) -> Callable:
        """注册一个在驱动器停止时执行的函数"""
        raise NotImplementedError

