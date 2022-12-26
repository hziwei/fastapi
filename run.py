import os

import test_fastapi
from test_fastapi.api import register_route
from test_fastapi.utils.sentry import configure_extensions
from test_fastapi.utils.log import logger


def _get_settings_file(env_name):
    env_settings_file_map = {
        "dev": "./configs/setting.cfg",
        "ubuntu": "./configs/setting-ubuntu.cfg",
        "test": "./configs/setting.cfg",
        "prod": "./configs/setting.cfg",
    }
    return env_settings_file_map.get(env_name, "./configs/setting.cfg")


def build_app():
    env_dist = os.environ
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--env_name", dest="env_name", default="ubuntu")

    (options, args) = parser.parse_args()
    _env_space_name = env_dist.get("ENV_NAME")
    if _env_space_name is None:
        _env_space_name = options.env_name
    logger.info(f"环境：{_env_space_name}")
    _settings_file = _get_settings_file(env_name=_env_space_name)
    # 初始化驱动和依赖
    test_fastapi.init(_env_file=_settings_file)
    # 注册路由
    register_route()
    app = test_fastapi.get_asgi()
    config = test_fastapi.get_config()

    # 设置sentry
    configure_extensions(env=config.env,
                         sentry_enabled=config.sentry_enabled,
                         sentry_dsn=config.sentry_dsn)
    return app
    pass


if __name__ == '__main__':
    app = build_app()
    test_fastapi.run(app=app)
