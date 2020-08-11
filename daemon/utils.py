import shortuuid
import base64
import os

read_env = lambda property: os.environ.get(property, None)

def enncode_int_id(message):
    pass

def decode_int_id(message):
    pass


def get_uuid():
    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
    return shortuuid.uuid()


def encode(message):
    if not message:
        return ""
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.a85encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return str(base64_message)


def decode(base64_message):
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.a85decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return str(message)





