import logging
from kombu import Exchange, Queue
from typing import Callable, Optional

from celery import Celery

from test_fastapi.utils.config import Config
from .basedriver import BaseDriver
from test_fastapi.utils import threaded


class CeleryDriver(BaseDriver):
    """Celery 驱动框架"""

    def __init__(self, config: Config):
        super(CeleryDriver, self).__init__(config)
        self._server_app = Celery(
            'celery_test',
            backend=config.celery_backend,
            broker=config.celery_broker,
            include=['test_fastapi.workers.tasks']
        )
        self._config()

    def _config(self):
        """celery 配置"""
        self._server_app.conf.task_acks_late = True
        self._server_app.conf.worker_prefetch_multiplier = 1
        # 任务序列化和反序列化使用msgpack方案
        self._server_app.conf.celery_task_serializer = "json"
        # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
        self._server_app.conf.celery_result_serializer = "json"
        # 指定接收的内容类型
        self._server_app.conf.celery_accept_content = ["json"]
        # 设置并发数
        self._server_app.conf.celery_concurrency = 5
        # 设置时区
        self._server_app.conf.timezone = 'Asia/Shanghai'
        self._server_app.conf.enable_utc = False
        self._server_app.conf.use_tz = True
        self._server_app.conf.celery_timezone = "Asia/Shanghai"
        # 某个程序中出现的队列，在broker中不存在，则立刻创建它
        self._server_app.conf.celery_create_missing_queues = True
        # 可以防止死锁
        self._server_app.conf.celeryd_force_execv = True
        # 任务结果过期时间(默认一天)
        self._server_app.conf.celery_task_result_expires = 3600
        # backen 缓存结果数目（默认5000）
        self._server_app.conf.celery_max_cached_results = 10000
        self._server_app.conf.broker_transport_options = {'visibility_timeout': 60}
        # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
        self._server_app.conf.celery_disable_rate_limits = True
        # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
        self._server_app.conf.celeryd_max_tasks_per_child = 100
        # 设置不同的队列
        self._server_app.conf.celery_queues = (
            Queue('dispatch-ca-daq-queue', Exchange('dispatch-ca-daq-queue'),
                  routing_key='dispatch-ca-daq-queue'),
            Queue('sichuang-ca-daq-queue', Exchange('sichuang-ca-daq-queue'),
                  routing_key='sichuang-ca-daq-queue'),
            Queue('dispatch-its-daq-queue', Exchange('dispatch-its-daq-queue'),
                  routing_key='dispatch-its-daq-queue'),
            Queue('hubei-its-daq-queue', Exchange('hubei-its-daq-queue'),
                  routing_key='hubei-its-daq-queue'),
        )
        # 不同任务分配不同队列
        self._server_app.conf.celery_routes = {
            'test_fastapi.workers.tasks.dingding_notice_task': {'queue': 'dispatch-ca-daq-queue',
                                                                  'routing_key': 'dispatch-ca-daq-queue'},
            'test_fastapi.workers.tasks.dingding_notice_task2': {'queue': 'sichuang-ca-daq-queue',
                                                                      'routing_key': 'sichuang-ca-daq-queue'},
            'celery_workers.its.dispatch_task.dispatch_dashboard': {'queue': 'dispatch-its-daq-queue',
                                                                         'routing_key': 'dispatch-its-daq-queue'},
            'celery_workers.its.hubei_dashbord_tax.hubei_dashbord_login': {'queue': 'hubei-its-daq-queue',
                                                                                'routing_key': 'hubei-its-daq-queue'},
        }
        pass

    @property
    def type(self) -> str:
        """ 驱动名称 fastapi"""
        return "celery"

    @property
    def server_app(self) -> Celery:
        """`Celery APP` 对象"""
        return self._server_app

    @property
    def asgi(self) -> Celery:
        """`Celery APP` 对象"""
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        """Celery 使用的 logger"""
        return logging.getLogger("celery")

    def on_startup(self, func: Callable) -> Callable:
        """celery """
        return self.server_app.start()

    def on_shutdown(self, func: Callable) -> Callable:
        """celery """
        return self.server_app.close()

    @threaded
    def run(
            self,
            *,
            app: Optional[str] = None,
            **kwargs,
    ):
        """启动 celery"""
        self.logger.info("celery start...")
        self.server_app.worker_main(argv=["worker",
                                     "--loglevel=info",
                                     "--concurrency=9",
                                     "--without-heartbeat",
                                     # "--without-gossip",
                                     "--without-mingle",
                                     "--pool=eventlet",
                                     # gevent solo
                                     "--pool=solo",
                                     ]
                               )
    pass


def test():
    config = Config()
    c = CeleryDriver(config)
    c.run()
    pass
