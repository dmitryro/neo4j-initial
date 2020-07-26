import base64
import os

def enncode_int_id(message):
    pass

def decode_int_id(message):
    pass

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


def read_env(property):
    """ Read environment """
    return os.environ.get(property, None)
