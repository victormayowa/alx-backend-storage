#!/usr/bin/env python3
"""
Module with get_page function.
"""
import requests
import redis
from typing import Optional


def cache_key(url: str) -> str:
    """
    Generates cache key for the given URL.
    """
    return f"count:{url}"


def get_page(url: str) -> str:
    """
    Obtains the HTML content of a URL and caches the result with a 10-second expiration time.
    """
    cache = redis.Redis()
    count_key = cache_key(url)
    
    # Check if the result is cached
    cached_result = cache.get(url)
    if cached_result:
        # Increment access count
        cache.incr(count_key)
        return cached_result.decode('utf-8')

    # Make the request
    response = requests.get(url)

    # Cache the result with a 10-second expiration time
    cache.setex(url, 10, response.text)

    # Increment access count
    cache.incr(count_key)

    return response.text