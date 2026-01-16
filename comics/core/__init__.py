"""
:copyright: (c) 2026 0xSi23
:license: MIT, see LICENSE for more details.
"""

from __future__ import annotations

from .connector_manager import ConnectorManager
from .base_connector import BaseConnector
from .models import Comic, Chapter, Image

__all__ = [
    "BaseConnector",
    "ConnectorManager",
    "Comic",
    "Chapter",
    "Image",
]