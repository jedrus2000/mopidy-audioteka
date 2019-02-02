# -*- coding: utf-8 -*-
import sys


class AudiotekaError(Exception):
    pass


def exception_guard(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            et, ei, tb = sys.exc_info()
            raise AudiotekaError, AudiotekaError(e), tb
    return wrapper