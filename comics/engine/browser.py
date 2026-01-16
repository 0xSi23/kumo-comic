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

from typing import Optional, Literal, TYPE_CHECKING
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth

from ..utils import random_delay, get_random_user_agent
from ..exceptions import BrowserNotStartedError, BrowserNavigationError, CloudflareBlockedError

import asyncio


class StealthBrowser:
    """
    Playwright browser wrapper with anti-detection features.
    - Random User-Agent rotation
    - Stealth mode to bypass Cloudflare
    - Auto-scroll for lazy-loading images
    - Random delays between actions
    """

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._user_agent: str = ""
        self._stealth: Optional[Stealth] = None

    
    async def start(self, headless: bool = True) -> None:
        """|coro|
        
        Launch browser with stealth settings.

        Parameters
        ----------
        headless: :class:`bool`
            Whether to run browser in headless mode. Defaults to ``True``.
        """

        self._user_agent = get_random_user_agent()
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        self.context = await self.browser.new_context(
            user_agent=self._user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh',
        )
        
        # Apply stealth patches
        self._stealth = Stealth()
        await self._stealth.apply_stealth_async(self.context)

        # Patch for CHR_MEMORY detection (navigator.deviceMemory)
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,  // 8GB RAM
                configurable: true
            });
        """)
        
        self.page = await self.context.new_page()

    
    async def navigate(
        self, 
        url: str, 
        wait_for: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded"
    ) -> None:
        """|coro|

        Navigate to URL and wait for page load.

        Includes random delay to appear more human-like.

        Parameters
        ----------
        url: :class:`str`
            The URL to navigate to.
        
        wait_for: :class:`Literal["commit", "domcontentloaded", "load", "networkidle"]`
            The event to wait for before considering navigation complete. 
            Defaults to ``"domcontentloaded"``.

        Raises
        ------
        :class:`BrowserNotStartedError`
            If the browser has not been started.
        
        :class:`BrowserNavigationError`
            If navigation to the URL fails.
        """

        if not self.page:
            raise BrowserNotStartedError()

        try:
            await self.page.goto(url, wait_until=wait_for, timeout=60000)
            await random_delay(1, 2)
        except Exception as e:
            raise BrowserNavigationError(url, str(e)) from e    


    async def wait_for_cloudflare(self, timeout: int = 30, raise_on_block: bool = False) -> bool:
        """
        Wait for Cloudflare challenge to complete.
        
        Parameters
        ----------
        timeout: :class:`int`
            Max seconds to wait for challenge. Defaults to ``30`` seconds.

        raise_on_block: :class:`bool`
            If True, raise :class:`CloudflareBlockedError` on timeout. 
            Defaults to ``False``.
        
        Returns
        -------
        :class:`bool`
            True if passed, False if timeout (when ``raise_on_block=False``).
        
        Raises
        ------
        :class:`BrowserNotStartedError`
            If browser not started.

        :class:`CloudflareBlockedError`
            If blocked and ``raise_on_block=True``.
        """

        if not self.page:
            raise BrowserNotStartedError()
        
        current_url = self.page.url
        
        # Wait for Cloudflare challenge to disappear
        cf_selectors = [
            "#challenge-running",
            ".cf-browser-verification",
            "#cf-please-wait",
        ]
            
        cf_detected = False
        for selector in cf_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    cf_detected = True
                    await self.page.wait_for_selector(
                        selector, 
                        state="hidden", 
                        timeout=timeout * 1000
                    )
            except asyncio.TimeoutError:
                if raise_on_block:
                    raise CloudflareBlockedError(current_url)
                return False
            
        await random_delay(1, 2)
        return True
    

    async def scroll_to_bottom(self, step: int = 500, delay: float = 0.3) -> None:
        """|coro|

        Scroll page to bottom to trigger lazy-loading images.

        Uses smooth scrolling with random delays.

        Parameters
        ----------
        step: :class:`int`
            Number of pixels to scroll per step. Defaults to ``500``.

        delay: :class:`float`
            Delay in seconds between scroll steps. Defaults to ``0.3``.

        Raises
        ------
        :class:`BrowserNotStartedError`
            If the browser has not been started.
        """

        if not self.page:
            raise BrowserNotStartedError()
        
        # Get page height
        prev_height = 0
        while True:
            current_height = await self.page.evaluate("document.body.scrollHeight")
            
            if current_height == prev_height:
                break
            
            prev_height = current_height
            
            # Scroll in steps
            scroll_position = 0
            while scroll_position < current_height:
                scroll_position += step
                await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
                await asyncio.sleep(delay + (asyncio.get_event_loop().time() % 0.2))
            
            # Wait for new content to load
            await random_delay(0.5, 1)


    async def close(self) -> None:
        """|coro| 
        
        Clean up browser resources.
        """

        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None