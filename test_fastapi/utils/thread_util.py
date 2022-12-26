from functools import wraps
from threading import Thread


def threaded(func):
    """线程启动"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()

    return wrapper
