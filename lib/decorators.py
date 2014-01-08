from functools import wraps
from pickle import loads, dumps


def cached(key, redis):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rv = redis.get(key)
            if rv is not None:
                return loads(rv)
            rv = f(*args, **kwargs)
            redis.set(key, dumps(rv))
            return rv
        return decorated_function
    return decorator
