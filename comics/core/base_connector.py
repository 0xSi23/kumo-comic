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

from typing import List, Optional, TYPE_CHECKING
from playwright.async_api import Page
from abc import ABC, abstractmethod

from ..exceptions import BrowserNotStartedError

if TYPE_CHECKING:
    from .models import Comic, Chapter
    from ..engine import StealthBrowser


class BaseConnector(ABC):
    """
    Abstract base class for website connectors.
    Each website should have its own connector inheriting from this class.
    """
    
    name: str = "Unknown"
    base_url: str = ""
    keyword = ""
    

    def __init__(self):
        self.browser: Optional["StealthBrowser"] = None

    
    @property
    def page(self) -> Page:
        """Get the current browser page.
        
        Raises
        ------
        :class:`BrowserNotStartedError`
            If the browser is not initialized.
        """

        self._ensure_browser()
        return self.browser.page
    

    def can_handle(self, url: str) -> bool:
        """
        Check if this connector can handle the given URL.
        
        Parameters
        ----------
        url: :class:`str`
            The URL to check.

        Returns
        -------
        :class:`bool`
            True if this connector can handle the URL, False otherwise.
        """

        return self.keyword in url

    
    @abstractmethod
    async def get_comic_info(self, url: str) -> "Comic":
        """|coro|
        Fetch comic information from URL.

        Parameters
        ----------
        url: :class:`str`
            The URL of the comic.

        Returns
        -------
        :class:`Comic`
            The comic information.
        """

        pass


    @abstractmethod
    async def get_chapter_images(self, chapter: "Chapter") -> List[str]:
        """|coro|
        Fetch all image URLs from a chapter.
        
        Parameters
        ----------
        chapter: :class:`Chapter`
            The chapter to fetch images from.

        Returns
        -------
        :class:`List[str]`
            List of image URLs in the chapter.
        """

        pass

    
    def _ensure_browser(self) -> None:
        """Ensure browser is initialized before operations.
        
        Raises
        ------
        :class:`BrowserNotStartedError`
            If the browser is not initialized.
        """
        if self.browser is None:
            raise BrowserNotStartedError()

    
    def init_browser(self, browser: "StealthBrowser") -> None:
        """
        Initialize browser reference
        
        Parameters
        ----------
        browser: :class:`StealthBrowser`
            The browser to use.
        """

        self.browser = browser
    

    def close(self):
        """Cleanup resources"""

        self.browser = None
