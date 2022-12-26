import os
import random
from typing import Optional

from fastapi import APIRouter

from test_fastapi import get_asgi
from .v1.views import api
import sentry_sdk
from sentry_sdk.tracing import Transaction
from test_fastapi.utils.sentry import set_trace_scope_tags, get_trace_headers

api_router = APIRouter()


def register_route():
    app = get_asgi()
    api_router.include_router(api, tags=["token"])
    app.include_router(api_router, prefix="/test/api/v1")


@api_router.get("/healthcheck")
def healthcheck(id:Optional[int]=None):
    task_id = random.randint(10000, 99999)
    trace_id = random.randint(10000, 99999)
    trace = get_trace_headers()
    set_trace_scope_tags(task_id=task_id, trace_id=trace_id)
    transaction = Transaction.continue_from_headers(trace)
    with sentry_sdk.start_transaction(transaction) as t:
        t.name = "healthcheck"
        t.op = "workers"
        t.set_tag("task_id", task_id)
        t.set_tag("trace_id", trace_id)
        try:
            assert id, ValueError("id不能为空")
        except:
            t.set_status("failure")
        t.set_status("ok")

    return {"status": "ok"}


@api_router.get("/healthcheck1")
def healthcheck1(id: Optional[int] = None):
    task_id = random.randint(10000, 99999)
    trace_id = random.randint(10000, 99999)
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("version", "1.0.0")
        scope.set_tag("framework_version", "1.0.0")
        scope.set_tag("host_ip", "localhost")
        scope.set_tag("port", "8000")
        scope.set_tag("pid", os.getpid())
        scope.set_tag("task_id", task_id)
        scope.set_tag("trace_id", trace_id)

    task_id = random.randint(10000, 99999)
    with sentry_sdk.push_scope() as scope:
        scope.set_extra('debug', False)
        scope.set_tag("task_id", task_id)
        scope.set_level("info")
    assert id, ValueError("id不能为空")
    print(id)
    return {"status": "ok"}