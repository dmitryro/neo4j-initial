import os

def read_env(property):
    """ Read environment """
    return os.environ.get(property, None)
