#!/usr/bin/env python3
"""
Module with Cache class.
"""

import redis
import uuid
from typing import Union


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

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generates a random key,
        stores the input data in Redis using the key,
        and returns the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
