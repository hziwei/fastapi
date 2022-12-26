import logging
from typing import Union, List, Callable, Optional

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError, BaseSettings
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from test_fastapi.utils.config import Config
import test_fastapi.utils.error_code as ec
from .basedriver import BaseDriver


class FastConfig(BaseSettings):
    """FastAPI 驱动框架设置，详情参考 FastAPI 文档"""

    api_router_path : Optional[str] = "/test/api/v1"

    """`openapi.json` 地址，默认为 `None` 即关闭"""
    fastapi_openapi_url: Optional[str] = f"{api_router_path}/openapi.json"

    """`swagger` 地址，默认为 `None` 即关闭"""
    fastapi_docs_url: Optional[str] = f"{api_router_path}/docs"

    """`redoc` 地址，默认为 `None` 即关闭"""
    fastapi_redoc_url: Optional[str] = f"{api_router_path}/redoc"

    """是否包含适配器路由的 schema，默认为 `True`"""
    fastapi_include_adapter_schema: bool = True

    """开启/关闭冷重载"""
    fastapi_reload: bool = False

    """重载监控文件夹列表，默认为 uvicorn 默认值"""
    fastapi_reload_dirs: Optional[List[str]] = None

    """重载延迟，默认为 uvicorn 默认值"""
    fastapi_reload_delay: Optional[float] = None

    """要监听的文件列表，支持 glob pattern，默认为 uvicorn 默认值"""
    fastapi_reload_includes: Optional[List[str]] = None

    """不要监听的文件列表，支持 glob pattern，默认为 uvicorn 默认值"""
    fastapi_reload_excludes: Optional[List[str]] = None

    class Config:
        extra = "ignore"


async def not_found(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "[404]Not Found.", "success": False, "message_code": ec.ClientErrorCode.EXECUTE_ERROR}
    )


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """ http error """
    return JSONResponse({"message": exc.__repr__(), "success": False, "message_code": ec.ClientErrorCode.EXECUTE_ERROR},
                        status_code=exc.status_code)


async def http422_error_handler(
        _: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """ validation_error """
    return JSONResponse(
        {"message": exc.__repr__(), "success": False, "message_code": ec.ClientErrorCode.EXECUTE_ERROR},
        status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )


class FastDriver(BaseDriver):
    """FastAPI 驱动框架"""

    def __init__(self, config: Config):
        super(FastDriver, self).__init__(config)
        self.fastapi_config = FastConfig(**config.__dict__)
        self._server_app = FastAPI(
            openapi_url=self.fastapi_config.fastapi_openapi_url,
            docs_url=self.fastapi_config.fastapi_docs_url,
            redoc_url=self.fastapi_config.fastapi_redoc_url,
            exception_handlers={404: not_found},
        )
        self._server_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._server_app.add_exception_handler(HTTPException, http_error_handler)
        self._server_app.add_exception_handler(RequestValidationError, http422_error_handler)

    @property
    def type(self) -> str:
        """ 驱动名称 fastapi"""
        return "fastapi"

    @property
    def server_app(self) -> FastAPI:
        """`FastAPI APP` 对象"""
        return self._server_app

    @property
    def asgi(self) -> FastAPI:
        """`FastAPI APP` 对象"""
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        """fastapi 使用的 logger"""
        return logging.getLogger("fastapi")

    def on_startup(self, func: Callable) -> Callable:
        """参考文档: `Events <https://fastapi.tiangolo.com/advanced/events/#startup-event>`_"""
        return self.server_app.on_event("startup")(func)

    def on_shutdown(self, func: Callable) -> Callable:
        """参考文档: `Events <https://fastapi.tiangolo.com/advanced/events/#shutdown-event>`_"""
        return self.server_app.on_event("shutdown")(func)

    def run(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            *,
            app: Optional[str] = None,
            **kwargs,
    ):
        """使用 `uvicorn` 启动 FastAPI"""
        # super().run(host, port, app, **kwargs)
        uvicorn.run(
            app or self.server_app,  # type: ignore
            host=host or str(self.config.host),
            port=port or self.config.port,
            reload=self.fastapi_config.fastapi_reload,
            reload_dirs=self.fastapi_config.fastapi_reload_dirs,
            reload_delay=self.fastapi_config.fastapi_reload_delay,
            reload_includes=self.fastapi_config.fastapi_reload_includes,
            reload_excludes=self.fastapi_config.fastapi_reload_excludes,
            debug=(self.config.log_level == "DEBUG"),
            **kwargs,
        )
    pass

