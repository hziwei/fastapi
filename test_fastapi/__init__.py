import importlib
from typing import Optional, Any, Type

from test_fastapi.utils.config import Config
from test_fastapi.drivers.basedriver import BaseDriver
from test_fastapi.utils.log import init_logger, logger

_config: Optional[Config] = None
_driver: Optional[BaseDriver] = None
_celery_driver: Optional[BaseDriver] = None


def init(_env_file: Optional[str] = None) -> None:
    """全局初始化"""
    global _config
    global _driver
    global _celery_driver
    if not _driver:
        logger.success("驱动初始化")
        # 配置
        _config = Config(
            _env_file=_env_file
        )

        init_logger(log_sink_stdout=_config.log_sink_stdout,
                    log_sink_file=_config.log_sink_file,
                    log_file=_config.log_file_name)
        # FastAPI 驱动初始化
        DriverClass: Type[BaseDriver] = _resolve_combine_expr(_config.driver, "FastDriver")
        _driver = DriverClass(_config)
        # Celery 驱动初始化
        DriverClass: Type[BaseDriver] = _resolve_combine_expr(_config.celery_driver, "CeleryDriver")
        _celery_driver = DriverClass(_config)


def _resolve_combine_expr(obj_str: str, cls_str: str) -> Type[BaseDriver]:
    """获取驱动类"""
    drivers = obj_str.split("+")
    DriverClass = _resolve_dot_notation(
        drivers[0], cls_str, default_prefix="test_fastapi.drivers."
    )
    if len(drivers) == 1:
        logger.trace(f"Detected driver {DriverClass} with no mixins.")
        return DriverClass


def _resolve_dot_notation(
    obj_str: str, default_attr: str, default_prefix: Optional[str] = None
) -> Any:
    modulename, _, cls = obj_str.partition(":")
    if default_prefix is not None and modulename.startswith("~"):
        modulename = default_prefix + modulename[1:]
    module = importlib.import_module(modulename)
    if not cls:
        return getattr(module, default_attr)
    instance = module
    for attr_str in cls.split("."):
        instance = getattr(instance, attr_str)
    return instance


def get_config() -> Optional[Config]:
    """获取配置对象"""
    global _config
    if _config is None:
        return Config()
    return _config


def get_asgi() -> Any:
    """获取fastapi实例"""
    driver = get_driver()
    assert isinstance(
        driver, BaseDriver
    ), "asgi object is onlu available for reverse driver"
    return driver.asgi


def get_driver() -> BaseDriver:
    """获取fastapi驱动"""
    global _driver
    if _driver is None:
        raise ValueError("fastapi驱动没有初始化")
    return _driver


def get_celery_asgi() -> BaseDriver:
    """获取celery 驱动"""
    global _celery_driver
    assert isinstance(
        _celery_driver, BaseDriver
    ), "asgi object is onlu available for reverse driver"
    return _celery_driver.asgi


def get_celery_driver() -> BaseDriver:
    """获取celery 驱动"""
    global _celery_driver
    if _celery_driver is None:
        raise ValueError("celery驱动没有初始化")
    return _celery_driver


def run(*args: Any, **kwargs: Any) -> None:
    """启动"""
    logger.success("启动celery驱动")
    get_celery_driver().run(*args, **kwargs)
    logger.success("启动celery驱动成功")

    logger.success("启动fastapi驱动")
    get_driver().run(*args, **kwargs)
