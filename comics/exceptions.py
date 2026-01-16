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

from typing import List


class KumoComicError(Exception):
    """Base exception for all KumoComic errors."""
    pass


# ============================================================================
# Browser Errors
# ============================================================================

class BrowserError(KumoComicError):
    """Base exception for browser-related errors."""
    pass


class BrowserNotStartedError(BrowserError):
    """Raised when browser operations are attempted before starting the browser."""
    
    def __init__(self):
        super().__init__("Browser not started. Call start() first.")


class BrowserNavigationError(BrowserError):
    """Raised when navigation to a URL fails."""
    
    def __init__(self, url: str, reason: str = ""):
        self.url = url
        self.reason = reason
        
        message = f"Failed to navigate to: {url}"
        if reason:
            message += f" ({reason or 'No reason provided'})"
        
        super().__init__(message)


class CloudflareBlockedError(BrowserError):
    """Raised when Cloudflare challenge cannot be bypassed."""
    
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Cloudflare blocked access to: {url}")


# ============================================================================
# Connector Errors
# ============================================================================

class ConnectorError(KumoComicError):
    """Base exception for connector-related errors."""
    pass


class ConnectorNotFoundError(ConnectorError):
    """Raised when no connector is found for the given URL."""
    
    def __init__(self, url: str):
        self.url = url
        
        message = f"No connector found for URL: {url}"
        
        super().__init__(message)


# ============================================================================
# Content Errors
# ============================================================================

class ContentError(KumoComicError):
    """Base exception for content-related errors."""
    pass


class NoChaptersFoundError(ContentError):
    """Raised when no chapters are found on a manga page."""
    
    def __init__(self, comic_url: str):
        self.comic_url = comic_url
        super().__init__(f"No chapters found at: {comic_url}")


class NoImagesFoundError(ContentError):
    """Raised when no images are found on a chapter page."""
    
    def __init__(self, chapter_url: str):
        self.chapter_url = chapter_url
        super().__init__(f"No images found at: {chapter_url}")


# ============================================================================
# Download Errors
# ============================================================================

class DownloadError(KumoComicError):
    """Base exception for download-related errors."""
    pass


class TaskDownloadError(DownloadError):
    """
    Raised when a download task fails after all retry attempts.
    
    Contains all errors encountered during retries for debugging.
    
    Attributes
    ----------
    url: :class:`str`
        The URL that failed to download.

    original_errors: :class:`List[Exception]`
        List of exceptions encountered during each retry attempt.

    last_error: :class:`Optional[Exception]`
        The last exception encountered.

    attempts: :class:`int`
        The number of download attempts made.
    """
    
    def __init__(self, url: str, errors: List[Exception]):
        self.url = url
        self.original_errors = errors
        self.last_error = errors[-1] if errors else None
        self.attempts = len(errors)
        
        message = f"Failed to download {url} after {self.attempts} attempts"
        if self.last_error:
            message += f": {self.last_error}"
        
        super().__init__(message)
        