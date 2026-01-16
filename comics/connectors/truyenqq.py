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
from typing import List, Union, Dict, overload, TYPE_CHECKING

from playwright.async_api import Page

from ..core.base_connector import BaseConnector
from ..core.models import Comic, Chapter, Image
from ..utils.helpers import random_delay
from ..exceptions import (
    NoChaptersFoundError,
    NoImagesFoundError,
)

import aiohttp
import re

class TruyenQQConnector(BaseConnector):
    """
    Connector for TruyenQQ website.
    Supports: truyenqqno.com and similar domains
    """
    
    name = "TruyenQQ"
    base_url = "https://truyenqqno.com"
    keyword = "truyenqq"
    
    # CSS Selectors
    CHAPTER_LIST_SELECTOR = ".works-chapter-item a, .list_chapter a"
    IMAGE_SELECTOR = ".chapter_content img"
    TITLE_SELECTOR = "h1"

    
    async def get_comic_info(self, url: str) -> Comic:
        """|coro|
        Fetch Comic information from Comic detail page URL.
        
        Example URL: https://truyenqqno.com/truyen-tranh/onepunch-man-244

        Parameters
        ----------
        url: :class:`str`
            The URL of the Comic detail page.

        Returns
        -------
        :class:`Comic`
            The Comic object with metadata and chapter list.
        """

        self._ensure_browser()
        
        await self.browser.navigate(url)
        # await self.browser.wait_for_cloudflare()
        
        page = self.browser.page
        
        data: Dict = await page.evaluate(f"""
            () => {{
                const titleEl = document.querySelector('{self.TITLE_SELECTOR}');
                const title = titleEl ? titleEl.innerText.trim() : 'Unknown Comic';
                
                const chapterEls = document.querySelectorAll('{self.CHAPTER_LIST_SELECTOR}');
                const chapters = Array.from(chapterEls).map((el, i) => {{
                    const href = el.getAttribute('href') || '';
                    const text = el.innerText.trim();
                    return {{ url: href, title: text }};
                }}).filter(c => c.url && c.title);
                
                return {{ title, chapters }};
            }}
        """)
        
        title = data.get('title', 'Unknown Comic')
        raw_chapters: List[Dict[str, str]] = data.get('chapters', [])
        
        chapters = []
        for i, ch in enumerate(raw_chapters):
            chapter_url = ch['url']
            chapter_title = ch['title']
            
            # Extract chapter ID from URL
            chapter_id = self._extract_chapter_id(chapter_url, i)
            
            # Make URL absolute if needed
            if not chapter_url.startswith("http"):
                chapter_url = self.base_url + chapter_url
            
            chapters.append(Chapter(
                id=chapter_id,
                title=chapter_title,
                url=chapter_url
            ))
        
        if not chapters:
            raise NoChaptersFoundError(url)

        return Comic(
            title=title,
            url=url,
            chapters=chapters
        )
    

    @overload
    async def get_chapter_images(self, chapter: Chapter) -> List[Image]: ...
    
    @overload
    async def get_chapter_images(self, chapter: str) -> List[Image]: ...

    async def get_chapter_images(self, chapter: Union[Chapter, str]) -> List[Image]:
        """|coro|
        Fetch all image URLs from a chapter.
        
        Example URL: https://truyenqqno.com/truyen-tranh/onepunch-man-244-chap-268.html

        Parameters
        ----------
        chapter: Union[:class:`Chapter`, :class:`str`]
            The chapter object or chapter URL to fetch images from.

        Returns
        -------
        :class:`List[str]`
            List of image URLs in the chapter.
        """

        # Convert URL string to Chapter object
        if isinstance(chapter, str):
            chapter = Chapter(
                id=self._extract_chapter_id(chapter, 0),
                title="",
                url=chapter
            )

        self._ensure_browser()
        
        await self.browser.navigate(chapter.url)
        # await self.browser.wait_for_cloudflare()
        
        # Scroll to load images
        # await self.browser.scroll_to_bottom(step=300, delay=0.2)
        # await random_delay(0.5, 1)
        
        # Extract image URLs
        image_urls = await self._extract_image_urls(self.browser.page)
        
        if not image_urls:
            raise NoImagesFoundError(chapter.url)

        for idx, url in enumerate(image_urls):
            chapter.images.append(Image(
                url=url,
                index=idx
            ))
        
        return chapter.images
    

    async def _extract_image_urls(self, page: Page) -> List[str]:
        """|coro|
        
        Extract images using JavaScript for performance.
        
        Parameters
        ----------
        page: :class:`Page`
            The Playwright page object.

        Returns
        -------
        :class:`List[str]`
            List of image URLs.
        """
        
        try:
            result = await page.evaluate(f"""
                () => {{
                    const images = Array.from(document.querySelectorAll('{self.IMAGE_SELECTOR}'));
                    if (!images.length) return [];
                    
                    const attrs = ['src', 'data-cdn', 'data-original'];
                    
                    return images.map(img => {{
                        for (const attr of attrs) {{
                            const url = img.getAttribute(attr);

                            // Filter out invalid URLs
                            if (url && url.startsWith('http') 
                                && !url.split('?')[0].includes('.gif')) return url;
                        }}
                        return '';
                    }}).filter(Boolean);
                }}
            """)
            return result if result else []
        except Exception:
            return []
    

    def _extract_chapter_id(self, url: str, index: int) -> str:
        """
        Extract chapter ID from URL
        
        Examples:
        - ...-chap-45.html -> 45
        - ...-chapter-48-2.html -> 48.2

        Parameters
        ----------
        url: :class:`str`
            The chapter URL.

        index: :class:`int`
            The index of the chapter in the list (for fallback).

        Returns
        -------
        :class:`str`
            The extracted chapter ID.
        """

        # Try to find chap-X pattern
        match = re.search(r'chap-(\d+(?:-\d+)?)', url, re.IGNORECASE)
        if match:
            return f"{str(match.group(1))}"
        
        # Try to find chapter-X pattern
        match = re.search(r'chapter-(\d+(?:-\d+)?)', url, re.IGNORECASE)
        if match:
            return f"{str(match.group(1))}"
        
        # Fallback to index
        return str(index + 1)
    