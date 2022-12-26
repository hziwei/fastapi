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
    # traces_sample_rate=1.0,
    # ignore_errors=[],  todo
)

task_id = random.randint(10000, 99999)


with sentry_sdk.configure_scope() as scope:
    scope.set_tag("version", "1.0.0")
    scope.set_tag("framework_version", "1.0.0")
    scope.set_tag("host_ip", "localhost")
    scope.set_tag("port", "8000")
    scope.set_tag("pid", os.getpid())
    scope.set_tag("task_id", task_id)

#
# # task_id = random.randint(10000, 99999)
with sentry_sdk.push_scope() as scope:
    scope.set_extra('debug', False)
    scope.set_tag("task_id", task_id)
    scope.set_level("transaction")

    sentry_sdk.capture_message('test1', 'transaction')
print(f"task_id={task_id}")

# <Transaction(name='', op=None, trace_id='9abf6fe3e47449e3bbc8b87a80118709', span_id='a052583f8e610699', parent_span_id=None, sampled=False)>
# <Transaction(name='', op=None, trace_id='9abf6fe3e47449e3bbc8b87a80118709', span_id='b9741bfcded595cc', parent_span_id='a052583f8e610699', sampled=None)>
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
#
#
t = get_trace_headers('pipeline')

transaction = Transaction.continue_from_headers(t)

with sentry_sdk.start_transaction(transaction) as t:
    t.name = "test1"
    t.op = "parent"
    t.set_tag("task_id", task_id)
    t.set_tag("task_id", t.trace_id)
    # t.set_tag("trace_id", trace_id)
    t.set_data('t', '12432')
    t.set_status("ok")

with transaction.start_child(op="child", description="end") as span:
    span.set_tag("task_id", task_id)
    span.set_tag("trace_id", span.trace_id)
    _status = "ending"

transaction.set_status("ok")
transaction.finish()


# audit = argv[1]
# assert audit == '1', Exception("测试错误")
print("这是正常结果！")