import os
from typing import Dict

import requests
import sentry_sdk
from sentry_sdk.tracing import Transaction

from test_fastapi.utils import logger
from test_fastapi import get_celery_asgi
from test_fastapi.utils import set_trace_scope_tags, get_trace_headers

server_app = get_celery_asgi()


@server_app.task()
def dingding_notice_task(js: Dict, task_id, trace_id):
    # trace = get_trace_headers("exec pipeline")
    # set_trace_scope_tags(task_id=task_id, trace_id=trace_id)
    # transaction = Transaction.continue_from_headers(trace)
    d = {
        "version": "1.0.0",
        "name": "run task",
        "host_ip": "localhost",
        "port": "8000",
        "pid": os.getpid(),
        "task_id": task_id,
        "trace_id": trace_id,
    }
    set_trace_scope_tags(**d)

    with sentry_sdk.start_transaction(name="run task", op="run workers", trace_id=trace_id, sampled=True) as t:
        t.name = "run task"
        t.op = "run workers"
        t.set_tag("task_id", task_id)
        t.set_tag("trace_id", trace_id)
        try:
            url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxx"
            js = str(js)
            logger.info(f"钉钉业务记录:{js}")
            # print(driver.logger.info(f"钉钉业务记录:{js}"))
            js = {"msgtype": "text", "text": {"content": f"业务报警,:{js}"}}
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            }
            res = requests.post(url, headers=headers, json=js)
        except:
            t.set_status("failure")
        t.set_status("ok")
    return res.json()
    pass


@server_app.task()
def dingding_notice_task2(js: Dict, task_id, trace_id):
    trace = get_trace_headers("exec pipeline")
    set_trace_scope_tags(task_id=task_id, trace_id=trace_id)
    transaction = Transaction.continue_from_headers(trace)
    with sentry_sdk.start_transaction(transaction) as t:
        t.name = "task pipeline"
        t.op = "workers"
        t.set_tag("task_id", task_id)
        t.set_tag("trace_id", trace_id)
        try:
            url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxx"
            js = str(js)
            logger.info(f"钉钉业务记录2:{js}")
            # print(driver.logger.info(f"钉钉业务记录:{js}"))
            js = {"msgtype": "text", "text": {"content": f"业务报警,:{js}"}}
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            }
            res = requests.post(url, headers=headers, json=js)
        except:
            t.set_status("failure")
        t.set_status("ok")
    return res.json()
    pass
