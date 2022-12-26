import os
import random
import logging

import sentry_sdk
from sentry_sdk.tracing import Transaction
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)
# 初始化操作===================================================================================
sentry_sdk_url = "http://758ff93e86034309877973d6fea02272@192.168.238.129:9000/2"
sentry_sdk.init(
    dsn=sentry_sdk_url,
    environment='dev',
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
    # default_integrations=False,
    # auto_enabling_integrations=False,
    traces_sample_rate=1.0,
    # #
    # # 个人身份信息
    # send_default_pii=True,
    # release='1.1.0',
)
# 记录开始1-生成跟踪对象=================================================================================================
task_id = random.randint(10000, 99999)
print(task_id)


def get_trace_headers(name: str = None) -> dict:
    t = sentry_sdk.Hub.current.scope.transaction
    if not t:
        t = sentry_sdk.start_transaction()
        t.name = "workers-pipeline" if not name else name
        t.sampled = True
        # log.debug(f"Start new sentry trace transaction.")
        print("Start new sentry trace transaction.")
    headers = dict(sentry_sdk.Hub.current.iter_trace_propagation_headers(t))
    # log.debug(f"Sentry-trace: {headers}")
    print(f"Sentry-trace: {headers}")
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


trace = get_trace_headers()

transaction = Transaction.continue_from_headers(trace)
trace_id = transaction.trace_id
# 记录开始===========================================================================================

print(trace_id)
d = {
    "version": "1.0.0",
    "name": "start pipe",
    "host_ip": "localhost",
    "port": "8000",
    "pid": os.getpid(),
    "task_id": task_id,
    "trace_id": trace_id,
}
set_trace_scope_tags(**d)
with sentry_sdk.start_transaction(transaction) as t:
    t.name = "start task"
    t.op = "start workers"
    t.description = "start"
    t.sampled = True
    t.set_tag("task_id", task_id)
    t.set_tag("trace_id", trace_id)
    try:
        print(1)
        with t.start_child(op="child", description="child1") as c:
            c.set_tag("task_id", task_id)
            with c.start_child(op="child-child", description="child2") as cc:
                cc.set_tag("task_id", task_id)
    except:
        print(1)
        t.set_status("failure")
    t.set_status("ok")
# child=========================================
# d = {
#     "version": "1.0.0",
#     "name": "start pipe",
#     "host_ip": "localhost",
#     "port": "8000",
#     "pid": os.getpid(),
#     "task_id": task_id,
#     "trace_id": trace_id,
# }
# set_trace_scope_tags(**d)
trace_headers = dict(sentry_sdk.Hub.current.iter_trace_propagation_headers(transaction))
transaction = Transaction.continue_from_headers(trace_headers)
with sentry_sdk.start_transaction(transaction) as t:
    t.name = "run task"
    t.op = "run workers"
    t.description = "run"
    t.sampled = True
    t.set_tag("task_id", task_id)
    t.set_tag("trace_id", trace_id)
    t.set_status("failure")
    t.set_status("ok")
# 第二个记录==================================================================================================
# d = {
#     "version": "1.0.0",
#     "name": "start pipe",
#     "host_ip": "localhost",
#     "port": "8000",
#     "pid": os.getpid(),
#     "task_id": task_id,
#     "trace_id": trace_id,
# }
# set_trace_scope_tags(**d)
with sentry_sdk.start_transaction(name="task parallel", op="parallel workers", trace_id=trace_id, sampled=True) as t:
    t.name = "task parallel"
    t.op = "workers"
    t.set_tag("task_id", task_id)
    try:
        print(1)
        with t.start_child(op="child", description="child1") as c:
            c.set_tag("task_id", task_id)
            with c.start_child(op="child-child", description="child2") as cc:
                cc.set_tag("task_id", task_id)
    except:
        t.set_status("failure")
    t.set_status("ok")
    trace_headers = dict(sentry_sdk.Hub.current.iter_trace_propagation_headers(t))
    transaction = Transaction.continue_from_headers(trace_headers)
    with sentry_sdk.start_transaction(transaction) as child_t:
        child_t.name = "task child parallel"
        child_t.op = "child workers"
        child_t.set_tag("task_id", task_id)
        try:
            print(1)
            with child_t.start_child(op="child", description="child1") as c:
                c.set_tag("task_id", task_id)
                with c.start_child(op="child-child", description="child2") as cc:
                    cc.set_tag("task_id", task_id)
        except:
            child_t.set_status("failure")
        child_t.set_status("ok")
# child============================================================================

