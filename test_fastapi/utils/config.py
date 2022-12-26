"""本模块定义了 TransBot 本身运行所需的配置项。

TransBot 使用 [`pydantic`](https://pydantic-docs.helpmanual.io/) 以及 [`python-dotenv`](https://saurabh-kumar.com/python-dotenv/) 来读取配置。

配置项需符合特殊格式或 json 序列化格式。详情见 [`pydantic Field Type`](https://pydantic-docs.helpmanual.io/usage/types/) 文档。

"""
import os
from pathlib import Path
from ipaddress import IPv4Address
from typing import TYPE_CHECKING, Any, Dict, Union, Mapping, Optional, Tuple
from configparser import ConfigParser

from pydantic import BaseSettings, IPvAnyAddress
from pydantic.env_settings import (
    EnvSettingsSource,
    InitSettingsSource,
    SettingsSourceCallable,
)


class CustomEnvSettings(EnvSettingsSource):
    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        """
        Build environment variables suitable for passing to the Model.
        """
        d: Dict[str, Optional[str]] = {}


        if settings.__config__.case_sensitive:
            env_vars: Mapping[str, Optional[str]] = os.environ  # pragma: no cover
        else:
            env_vars = {k.lower(): v for k, v in os.environ.items()}
        cfg = ConfigParser()

        env_file = f"{os.getcwd()}/{Path(self.env_file)}"
        cfg.read(env_file, encoding='utf8')
        for section in cfg.sections():
            for k, v in cfg[section].items():
                if section != "fastapi":
                    k = f"{section}_{k}"
                    pass
                d[k.lower()] = v
            pass
        return d


class BaseConfig(BaseSettings):
    if TYPE_CHECKING:
        # dummy getattr for pylance checking, actually not used
        def __getattr__(self, name: str) -> Any:  # pragma: no cover
            return self.__dict__.get(name)

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: InitSettingsSource,
            env_settings: EnvSettingsSource,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable,...]:
            return (
                CustomEnvSettings(
                    env_settings.env_file, env_settings.env_file_encoding
                ),
            )


class Config(BaseConfig):
    """TransBot 主要配置。大小写不敏感。

    除了框架的配置项外，还可以自行添加配置项到 `.env.{environment}` 文件中。
    这些配置将会在 json 反序列化后一起带入 `Config` 类中。

    """

    env: str = "dev"
    driver: str = "~fastapi"

    host: IPvAnyAddress = IPv4Address("0.0.0.0")  # type: ignore
    port: int = 13001

    debug: bool = False
    log_sink_stdout: bool = True
    log_sink_file: bool = True
    log_level: Union[int, str] = "INFO"
    log_file_name: str = "./logs/fastapi-{time}.log"

    sentry_enabled: bool = False
    sentry_dsn: str = "http://758ff93e86034309877973d6fea02272@localhost:9000/2"

    celery_driver: str = "~celeryapp"
    celery_backend = "redis://@127.0.0.1:6379/1"
    celery_broker = "redis://@127.0.0.1:6379/0"

    class Config:
        extra = "allow"
        env_file = ".env.prod"