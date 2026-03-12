# Minimal datetime stubs

from builtins import object

class datetime(object):
    @classmethod
    def utcnow(cls) -> "datetime": ...

class timedelta(object): ...
class date(object): ...
