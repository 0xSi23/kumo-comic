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
    List,
    List,
    Tuple,
    Optional, 
    Dict,
    Union,
)
from urllib.parse import urlparse

from ..utils import (
    random_delay, 
    maybe_coroutine, 
    get_image_extension as _get_img_ext,
    ensure_path
)
from ..core import DownloadTask, Chapter, Comic
from ..exceptions import TaskDownloadError

import asyncio
import aiohttp
import aiofiles


class ImageDownloader:
    """
    Async image downloader with rate limiting to avoid being blocked.
    Features:
    - Concurrent downloads with semaphore limit
    - Random delays between downloads
    - Referer header spoofing
    - Retry mechanism
    - Progress tracking

    Parameters
    ----------
    max_concurrent: :class:`int`
        Maximum number of concurrent downloads. Defaults to ``3``.
        
        .. note:: 
            Keep this low to avoid being blocked by anti-bot measures.

    delay_range: :class:`Optional[Tuple[float, float]]`
        Min and max delay (in seconds) between downloads. Use ``(x, 0.0)`` or ``None`` to effectively disable delay.
        Defaults to ``(1.0, 3.0)``.

    max_retries: :class:`int`
        Maximum number of retries for failed downloads. Defaults to ``3``.

    timeout: :class:`int`
        Timeout (in seconds) for each download request. Defaults to ``60``.

    default_headers: :class:`Optional[Dict[str, str]]`
        Default headers to include in each download request.
    """
    
    def __init__(
        self,
        max_concurrent: int = 3,  # Low to avoid being blocked
        delay_range: Optional[Tuple[float, float]] = (1.0, 3.0),
        max_retries: int = 3,
        timeout: int = 60,
        default_headers: Optional[Dict[str, str]] = None
    ):
        self.max_concurrent = max_concurrent
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.default_headers = default_headers or {}

        self._timeout = timeout

        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.__total_downloaded = 0
        self.__total_failed = 0


    @property
    def stats(self) -> Dict[str, int]:
        """Get download statistics."""

        return {
            "downloaded": self.__total_downloaded,
            "failed": self.__total_failed,
            "total": self.__total_downloaded + self.__total_failed
        }
    

    @property
    def timeout(self) -> int:
        """Get the timeout for download requests."""

        return self._timeout
    

    def set_timeout(self, timeout: int) -> None:
        """
        Set the timeout for download requests.

        Parameters
        ----------
        timeout: :class:`int`
            Timeout in seconds.
        """

        self.timeout = timeout

    
    def _build_headers(self, task: DownloadTask) -> Dict[str, str]:
        """
        Build headers for the download request, including `referer` if specified.

        Parameters
        ----------
        task: :class:`DownloadTask`
            The download task containing metadata.

        Returns
        -------
        :class:`Dict[str, str]`
            The headers for the download request.
        """
        
        headers = self.default_headers.copy()
        
        # Add task-specific headers
        headers.update(task.headers)
        
        # Add referer and origin if specified
        if task.referer:
            headers["Referer"] = task.referer

            parsed = urlparse(task.referer)
            headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
        
        return headers
    

    async def download_task(
        self,
        session: aiohttp.ClientSession,
        task: DownloadTask
    ) -> bool:
        """|coro|

        Download a single task with its own headers, cookies, save_path.
        
        Parameters
        ----------
        session: :class:`aiohttp.ClientSession`
            The aiohttp session to use for downloading.

        task: :class:`DownloadTask`
            The download task to process.

        Returns
        -------
        :class:`bool`
            True if download succeeded, False otherwise.
        """

        errors: List[Exception] = []

        async with self._semaphore:
            # Ensure parent directory exists
            task.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            for attempt in range(self.max_retries):
                try:
                    # Random delay before download
                    if self.delay_range:
                        await random_delay(*self.delay_range)
                    
                    headers = self._build_headers(task)
                    
                    async with session.get(
                        task.url,
                        headers=headers,
                        cookies=task.cookies or None,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            async with aiofiles.open(task.save_path, 'wb') as f:
                                await f.write(content)
                            
                            self.__total_downloaded += 1
                            
                            # Call success hook
                            await maybe_coroutine(task.on_success)
                            return True
                        
                        elif response.status == 429:
                            # Rate limited - wait longer
                            errors.append(Exception(f"HTTP 429: Rate limited"))
                            await random_delay(5, 10)
                            continue
                        
                        elif response.status == 403:
                            # Forbidden - might need different headers
                            errors.append(Exception(f"HTTP 403: Forbidden"))
                            await random_delay(2, 4)
                            continue
                        
                except Exception as e:
                    errors.append(e)
                    if attempt < self.max_retries - 1:
                        await random_delay(2, 5)
                        continue

                    break
            
            self.__total_failed += 1
            
            # Call error hook
            error = TaskDownloadError(task.url, errors)
            await maybe_coroutine(task.on_error, error)
            
            return False
        
    
    async def download_tasks(
        self, 
        tasks: List[DownloadTask]
    ) -> Tuple[int, int]:
        """|coro|

        Download multiple tasks concurrently.
        
        Each task can have its own save_path, headers, cookies, and referer.
        This enables downloading pages from different chapters simultaneously.
        
        Parameters
        ----------
        tasks: :class:`List[DownloadTask]`
            List of download tasks to process.
        
        Returns
        -------
        :class:`Tuple[int, int]`
            Tuple of (downloaded_count, failed_count)
        """

        downloaded_count = 0
        failed_count = 0
        
        async with aiohttp.ClientSession() as session:
            download_coroutines = [
                self.download_task(session, task)
                for task in tasks
            ]
            results = await asyncio.gather(*download_coroutines, return_exceptions=True)
        
        downloaded_count = results.count(True)
        failed_count = len(tasks) - downloaded_count

        self.__total_downloaded += downloaded_count
        self.__total_failed += failed_count

        return (downloaded_count, failed_count)
    