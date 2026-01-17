"""
MIT License

Copyright (c) 2026 0xSi23

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Awaitable, 
    Callable, 
    TypeVar, 
    ParamSpec, 
    Union, 
    TYPE_CHECKING
)
from inspect import isawaitable

import asyncio
import random



T = TypeVar("T")
P = ParamSpec("P")


async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """|coro|

    Introduce a random delay between ``min_seconds`` and ``max_seconds``.

    Helps avoid detection by making requests appear more human-like.

    Parameters
    -----------
    min_seconds: :class:`float` = 1.0
        Minimum delay in seconds. Defaults to ``1.0`` second.

    max_seconds: :class:`float` = 3.0
        Maximum delay in seconds. Defaults to ``3.0`` seconds.
    """
    
    if max_seconds <= 0.0:
        return
    
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def maybe_coroutine(
    func: Callable[P, Union[T, Awaitable[T]]], 
    *args: P.args, 
    **kwargs: P.kwargs
) -> T:
    """|coro|

    Execute a function that may be either synchronous or asynchronous.

    Also automatically detects the function's return type 
    and handles it appropriately.

    Parameters
    ----------
    func: :class:`Callable`
        The function or coroutine to execute.

    *args
        The arguments to pass to the function.

    **kwargs
        The keyword arguments to pass to the function.
        
    Returns
    -------
    Any
        The result of the function or coroutine.
    """
    
    result = func(*args, **kwargs)
    if isawaitable(result):
        return await result
    
    return result 


def get_image_extension(url: str) -> str:
    """
    Extract file extension from URL
        
    Parameters
    ----------
    url: :class:`str`
        The URL to extract extension from.
        
    Returns
    -------
    :class:`str`
        The file extension, including the dot (e.g. '.jpg').
    """

    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif']:
        if ext in url.lower():
            return ext
        
    return '.jpg'


def ensure_path(path: Union[str, Path]) -> Path:
    """
    Ensure the given path is a Path object.
    
    Parameters
    ----------
    path: :class:`Union[str, Path]`
        The path to ensure.

    Returns
    -------
    :class:`Path`
        The ensured Path object.
    """

    return Path(path) if isinstance(path, str) else path