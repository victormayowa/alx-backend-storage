#!/usr/bin/env python3

"""
Module with Cache class.
"""
import redis
import uuid
from typing import Callable, Union
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to methods of the Cache class.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to count calls.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for
    a particular function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store history.
        """
        input_key = "{}:inputs".format(method.__qualname__)
        output_key = "{}:outputs".format(method.__qualname__)

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, result)

        return result
    return wrapper


def replay(fn: Callable) -> None:
    """
    Displays the history of calls of a particular function.
    """
    key = fn.__qualname__
    inputs = cache._redis.lrange("{}:inputs".format(key), 0, -1)
    outputs = cache._redis.lrange("{}:outputs".format(key), 0, -1)

    print("{} was called {} times:".format(key, len(inputs)))

    for inp, out in zip(inputs, outputs):
        print("{} -> {}".format(fn(*eval(inp)), out.decode("utf-8")))


class Cache:
    """
    Cache class.
    """
    def __init__(self):
        """
        Initializes a Redis cache instance.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generates a random key,
        stores the input data in Redis using the key,
        and returns the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) ->
    Union[str, bytes, int, float, None]:
        """
        Retrieves the data from Redis using the provided key and
        optionally applies the conversion function.
        """
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieves a string from Redis using the provided key.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieves an integer from Redis using the provided key.
        """
        return self.get(key, fn=int)
