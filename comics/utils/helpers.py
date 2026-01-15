"""
MIT License

Copyright (c) 2026 - present 0xSi23

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

from typing import Optional, TYPE_CHECKING
import asyncio
import random
import re

async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """|coro|

    Sleep for a random duration between min and max seconds.

    Helps avoid detection by making requests appear more human-like.

    Parameters
    -----------
    min_seconds: :class:`float` = 1.0
        The minimum number of seconds to sleep. Defaults to ``1.0`` seconds.

    max_seconds: :class:`float` = 3.0
        The maximum number of seconds to sleep. Defaults to ``3.0`` seconds.
    """

    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)