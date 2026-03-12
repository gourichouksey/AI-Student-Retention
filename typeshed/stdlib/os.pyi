# Minimal os stubs

from builtins import str, object

def getenv(key: str, default: object = ...) -> object: ...

class path(object):
    @staticmethod
    def join(*args: str) -> str: ...
    @staticmethod
    def dirname(p: str) -> str: ...
