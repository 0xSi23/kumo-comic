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

from typing import List, Optional, TYPE_CHECKING


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
            message += f" ({reason})"
        
        super().__init__(message)


class CloudflareBlockedError(BrowserError):
    """Raised when Cloudflare challenge cannot be bypassed."""
    
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Cloudflare blocked access to: {url}")
