
class AudiotekaError(Exception):
    pass


def exception_guard(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            raise AudiotekaError(e)
    return wrapper
