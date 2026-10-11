from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from launchlens.errors import APIError

P = ParamSpec("P")
R = TypeVar("R")


def timed(function: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            setattr(wrapper, "last_duration_ms", (time.perf_counter() - started) * 1000)
    setattr(wrapper, "last_duration_ms", 0.0)
    return wrapper


def retry_api(attempts: int = 3):
    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(attempts):
                try:
                    return function(*args, **kwargs)
                except APIError as error:
                    if error.status_code not in {408, 429, 500, 502, 503, 504} or attempt == attempts - 1:
                        raise
                    time.sleep(0.2 * (attempt + 1))
            raise RuntimeError("unreachable")
        return wrapper
    return decorator