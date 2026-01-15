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

from typing import List
from dataclasses import dataclass, field

import re


@dataclass
class Page:
    """Represents a single page/image in a chapter"""
    index: int
    url: str
    filename: str = ""
    
    def __post_init__(self):
        if not self.filename:
            # Extract filename from URL or generate one
            self.filename = f"{self.index:03d}.jpg"


@dataclass
class Chapter:
    """Represents a comic chapter"""
    id: str
    title: str
    url: str
    pages: List[Page] = field(default_factory=list)
    
    @property
    def safe_title(self) -> str:
        """Return a filesystem-safe title"""

        # Remove invalid characters for Windows filesystem
        return re.sub(r'[<>:"/\\|?*]', '', self.title).strip()


@dataclass
class Comic:
    """Represents a comic series"""
    title: str
    url: str
    chapters: List[Chapter] = field(default_factory=list)
    cover_url: str = ""
    
    @property
    def safe_title(self) -> str:
        """Return a filesystem-safe title"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '', self.title).strip()
