import os
import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration

from test_fastapi.utils.log import logger


sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)


def _before_send(event, hint):
    # httplib_request
    logger.debug(f"_before_send: {event}, {hint}")
    return event


def configure_extensions(env, sentry_enabled, sentry_dsn, host_ip=None, run_port=None, version=None):
    """配置"""
    logger.debug("Configuring sentry extensions...")
    if sentry_enabled and sentry_dsn:
        _env = env
        sentry_sdk.init(
            dsn=str(sentry_dsn),
            integrations=[
                AtexitIntegration(),
                DedupeIntegration(),
                ExcepthookIntegration(),
                # ModulesIntegration(),
                # StdlibIntegration(),
                ThreadingIntegration(),
                ArgvIntegration(),
                sentry_logging,
            ],
            environment=_env,
            default_integrations=False,
            auto_enabling_integrations=False,
            traces_sample_rate=1.0,

            # 个人身份信息
            send_default_pii=True,
            release=version,
            # debug=True,
            # before_send=_before_send,
        )

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("version", version)
            scope.set_tag("host_ip", host_ip)
            scope.set_tag("port", run_port)
            scope.set_tag("pid", os.getpid())
    else:
        sentry_sdk.init(
            dsn=None,
            default_integrations=False,
            auto_enabling_integrations=False,
            sample_rate=0,
            traces_sample_rate=0,
            # ignore_errors=[],  todo
        )


def get_trace_headers(name: str = None) -> dict:
    """获取跟踪头"""
    t = sentry_sdk.Hub.current.scope.transaction
    if not t:
        t = sentry_sdk.start_transaction()
        t.name = "workers-pipeline" if not name else name
        t.sampled = True
        logger.debug(f"Start new sentry trace transaction.")
    headers = dict(sentry_sdk.Hub.current.iter_trace_propagation_headers(t))
    logger.debug(f"Sentry-trace: {headers}")
    return headers


def set_trace_scope_tags(**kwargs):
    """设置追踪标签"""
    if kwargs:
        # noinspection PyBroadException
        try:
            nsrsbh = kwargs.get("nsrsbh", "")
            nsrmc = kwargs.get("nsrmc", "")

            if not nsrmc:
                nsrmc = nsrsbh
            with sentry_sdk.configure_scope() as scope:
                scope.set_user({"id": nsrsbh, "username": nsrmc})
                for k, v in kwargs.items():
                    scope.set_tag(k, v)
                    sentry_sdk.set_tag(k, v)
        except Exception:  # pylint: disable=broad-except
            return