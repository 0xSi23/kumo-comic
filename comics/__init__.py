"""
KumoComic - A HakuNeko-inspired manga/comic downloader

This library provides a connector-based architecture for downloading
manga and comics from various websites.

:copyright: (c) 2026 0xSi23
:license: MIT, see LICENSE for more details.
"""

__title__ = "comics"
__author__ = "0xSi23"
__license__ = "MIT"
__copyright__ = "2026 0xSi23"
__version__ = "0.1.0"


from .engine import StealthBrowser

from .exceptions import (
    KumoComicError,
    BrowserError,
    BrowserNotStartedError,
    BrowserNavigationError,
    CloudflareBlockedError,
    ConnectorError,
    ConnectorNotFoundError
)
