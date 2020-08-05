import aiotools
import asyncio
import json
from functools import wraps
from time import sleep
from utils import r, ar
from threading import Thread
from functools import wraps
from time import sleep

try:
    import queue as Queue
except ImportError:
    import Queue as Queue


def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        queue = Queue.Queue()
        t = Thread(target=func, args=(queue,) + args, kwargs=kwargs)
        t.start()
        return queue, t

    return async_func


def async_timeout(s):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            async with timeout(s):
                return await f(*args, **kwargs)
        return wrapper
    return decorator


def daemonize(func, *, loop=None):
    def wraps(*args):
        _loop = loop if loop is not None else asyncio.get_event_loop()
        yield _loop.run_in_executor(executor=None, func=func, *args)
    return wraps


def on_approved(key):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
             print(f"KEY {key}")
             while True:
                 approved = []
                 while(r.llen(key)!=0):
                     item = r.lpop('approved')
                     d = json.loads(item)
                     approved.append(d)
                 if len(approved) > 0:
                     kwargs[key] = approved
                     return f(*args, **kwargs)
                 sleep(1.0)
        return wrapper
    return decorator

