import os
import random
from datetime import timedelta
from typing import Dict

from fastapi import Depends, APIRouter, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
import sentry_sdk
from sentry_sdk.tracing import Transaction

from test_fastapi.utils import set_trace_scope_tags, get_trace_headers
from .models import (
    User,
    Token,
    fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .service import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)

api = APIRouter()


@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    task_id = 111111
    trace_id = 2222222
    trace = get_trace_headers()
    set_trace_scope_tags(task_id=task_id, trace_id=trace_id)
    transaction = sentry_sdk.start_transaction(Transaction.continue_from_headers(trace))
    transaction.name = "task pipeline"
    transaction.op = "workers"
    transaction.set_tag("task_id", task_id)
    transaction.set_tag("trace_id", trace_id)
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@api.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@api.post("/test/")
async def dingding_notice(js: Dict=Body(..., title="test")):
    import test_fastapi.workers.tasks
    task_id = random.randint(10000, 99999)
    trace = get_trace_headers()
    set_trace_scope_tags(task_id=task_id)
    transaction = Transaction.continue_from_headers(trace)
    trace_id = transaction.trace_id
    d = {
        "version": "1.0.0",
        "name": "start task",
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
        t.set_tag("task_id", task_id)
        t.set_tag("trace_id", trace_id)
        try:
            res = test_fastapi.workers.tasks.dingding_notice_task.delay(js, task_id, trace_id)
        except:
            t.set_status("failure")
        t.set_status("ok")

    return {"text": res.id}
