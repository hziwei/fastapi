import os
import random
from sys import argv

import sentry_sdk
from sentry_sdk.tracing import Transaction

sentry_sdk_url = "http://758ff93e86034309877973d6fea02272@192.168.238.129:9000/2"
sentry_sdk.init(
    dsn=sentry_sdk_url,
    # default_integrations=False,
    # auto_enabling_integrations=False,
    # sample_rate=0,
    # traces_sample_rate=0,
    # ignore_errors=[],  todo
)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("version", "1.0.0")
    scope.set_tag("framework_version", "1.0.0")
    scope.set_tag("host_ip", "localhost")
    scope.set_tag("port", "8000")
    scope.set_tag("pid", os.getpid())


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


task_id = random.randint(10000, 99999)
trace_id = random.randint(100000, 999999)

transaction = sentry_sdk.start_transaction(Transaction.continue_from_headers(get_trace_headers()))
transaction.name = "test pipeline"
transaction.op = "workers"
transaction.set_tag("task_id", task_id)
transaction.set_tag("trace_id", trace_id)
transaction.set_tag("jylsh", '1234567')
transaction.set_tag("nsrsbh", '1234567')
transaction.set_tag("channel_id", '1111111')
print(f"task_id:{task_id}")
print(f"trace_id:{trace_id}")
print(f"transaction:{transaction}")

with transaction.start_child(op="pipeline", description="end") as span:
    span.set_tag("task_id", task_id)
    span.set_tag("trace_id", trace_id)
    _status = "ending"
    # audit = argv[1]
    #
    # assert audit == '1', Exception("测试错误")

    print("这是正常结果！")

transaction.set_status("ok")
transaction.finish()
