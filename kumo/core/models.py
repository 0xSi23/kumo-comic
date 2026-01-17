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

from typing import (
    List,
    Optional,
    Union,
    Awaitable,
    Dict,
    Any
)
from pathlib import Path
from dataclasses import dataclass, field

from ..exceptions import DownloadError
from ..utils import ensure_path

import re


@dataclass
class DownloadTask:
    """
    Self-contained download job with all metadata needed for download.
    
    Each task represents a single file to download with its own
    save path, headers, cookies, and referer.
    
    Hooks
    -----
    Override ``on_success()`` and ``on_error()`` in a subclass to handle
    download completion events. Both sync and async methods are supported.
    
    .. Example::
        ```
        @dataclass
        class MyTask(DownloadTask):
            async def on_success(self):
                print(f"Downloaded: {self.save_path}")

            def on_error(self, error):
                print(f"Failed: {self.url}")
        ```
    """
    
    url: str
    save_path: Union[str, Path]
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    referer: str = ""
    extras: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.save_path, str):
            self.save_path = Path(self.save_path)

    
    def on_success(self) -> Union[None, Awaitable[None]]:
        """
        
        Called when download completes successfully. Override in subclass."""

        pass
    
    def on_error(self, error: Optional[DownloadError]) -> Union[None, Awaitable[None]]:
        """
        Called when download fails after all retries. Override in subclass.

        Parameters
        ----------
        error: Optional[:class:`DownloadError`]
            The exception that caused the failure.        
        """

        pass


@dataclass
class Image:
    """Represents a single image in a chapter"""

    index: int
    url: str
    filename: str = ""
    
    def __post_init__(self):
        if not self.filename:
            self.filename = f"{self.index:03d}.jpg"
    

    def to_task(
        self,
        save_dir: Union[str, Path],
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        referer: str = "",
    ) -> DownloadTask:
        """
        Convert this image to a :class:`DownloadTask` with custom metadata.

        Parameters
        ----------
        save_dir: Union[:class:`str`, :class:`Path`]
            The directory to save the image in.

        headers: Optional[:class:`Dict[str, str]`]
            Optional headers to include in the download request.
            
        cookies: Optional[:class:`Dict[str, str]`]
            Optional cookies to include in the download request.

        referer: str
            Optional referer header.

        Returns
        -------
        :class:`DownloadTask`
            The download task for this image.
        """

        save_dir = ensure_path(save_dir)
        return DownloadTask(
            url=self.url,
            save_path=save_dir / self.filename,
            headers=headers or {},
            cookies=cookies or {},
            referer=referer,
            extras={"index": self.index},
        )


@dataclass
class Chapter:
    """Represents a comic chapter"""

    id: str
    title: str
    url: str
    images: List[Image] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)

    _loaded_images: bool = field(default=False, init=False)
    
    @property
    def safe_title(self) -> str:
        """Return a filesystem-safe title"""

        return re.sub(r'[<>:"/\\|?*]', '', self.title).strip()
    

    def to_download_tasks(self, save_dir: Union[str, Path]) -> List[DownloadTask]:
        """
        Convert all images in this chapter to a list of :class:`DownloadTask`.

        .. note:: 
            All tasks will use the same save directory, referer and headers/cookies.

        Parameters
        ----------
        save_dir: Union[:class:`str`, :class:`Path`]
            The directory to save the images in.

        Returns
        -------
        :class:`List[DownloadTask]`
            List of download tasks for all images in this chapter.
        """

        save_dir = ensure_path(save_dir)
        tasks = []
        
        for image in self.images:
            tasks.append(DownloadTask(
                url=image.url,
                save_path=save_dir / image.filename,
                headers=self.headers.copy(),
                cookies=self.cookies.copy(),
                referer=self.url,
                extras={"index": image.index}
            ))
        
        return tasks


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

        return re.sub(r'[<>:"/\\|?*]', '', self.title).strip()
