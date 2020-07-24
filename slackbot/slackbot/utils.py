# -*- coding: utf-8 -*-
import os
import logging
import tempfile
import requests
from time import sleep
from redis import StrictRedis as RegularStrictRedis
from contextlib import contextmanager
from six.moves import _thread, range, queue
import six
import base64

logger = logging.getLogger(__name__)
r = RegularStrictRedis(host='redis', port=6379, db=0)


def read_env(property):
    """ Read environment """
    return os.environ.get(property, None)


def encode(message):
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message


def decode(base64_message):
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message


def read_answer(msg):
    r.lpush('questions', msg)
    logger.info("Processing answer")
    sleep(4)
    key = encode(msg)
    answer_key = f'{key}-answer'
    answer = r.get(answer_key).decode('utf-8')
    return answer

def read_env(property):
    """ Read environment """
    return os.environ.get(property, None)


def download_file(url, fpath, token=''):
    logger.debug('starting to fetch %s', url)
    headers = {"Authorization": "Bearer "+token} if token else None
    r = requests.get(url, stream=True, headers=headers)
    with open(fpath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*64):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    logger.debug('fetch %s', fpath)
    return fpath


def to_utf8(s):
    """Convert a string to utf8. If the argument is an iterable
    (list/tuple/set), then each element of it would be converted instead.

    >>> to_utf8('a')
    'a'
    >>> to_utf8(u'a')
    'a'
    >>> to_utf8([u'a', u'b', u'\u4f60'])
    ['a', 'b', '\\xe4\\xbd\\xa0']
    """
    if six.PY2:
        if isinstance(s, str):
            return s
        elif isinstance(s, unicode):
            return s.encode('utf-8')
        elif isinstance(s, (list, tuple, set)):
            return [to_utf8(v) for v in s]
        else:
            return s
    else:
        return s


@contextmanager
def create_tmp_file(content=''):
    fd, name = tempfile.mkstemp()
    try:
        if content:
            os.write(fd, content)
        yield name
    finally:
        os.close(fd)
        os.remove(name)


class WorkerPool(object):
    def __init__(self, func, nworker=10):
        self.nworker = nworker
        self.func = func
        self.queue = queue.Queue()

    def start(self):
        for __ in range(self.nworker):
            _thread.start_new_thread(self.do_work, tuple())

    def add_task(self, msg):
        self.queue.put(msg)

    def do_work(self):
        while True:
            msg = self.queue.get()
            self.func(msg)


def get_http_proxy(environ):
    proxy, proxy_port, no_proxy = None, None, None

    if 'http_proxy' in environ:
        http_proxy = environ['http_proxy']
        prefix = 'http://'
        if http_proxy.startswith(prefix):
            http_proxy = http_proxy[len(prefix):]
        proxy, proxy_port = http_proxy.split(':')

    if 'no_proxy' in environ:
        no_proxy = environ['no_proxy']

    return proxy, proxy_port, no_proxy