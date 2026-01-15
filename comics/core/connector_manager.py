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
from pathlib import Path

from .base_connector import BaseConnector
from ..engine import StealthBrowser
from ..exceptions import ConnectorNotFoundError

import pkgutil
import importlib


class ConnectorManager:
    """Manages all available website connectors."""
    
    def __init__(self, browser: Optional["StealthBrowser"] = None):
        self._connectors: dict[str, BaseConnector] = {}
        self._browser = browser

        self._load_connectors()

    
    def _load_connectors(self) -> None:
        """Auto-discover and load all connectors from the connectors package"""

        from .. import connectors as connectors_pkg
        
        package_path = Path(connectors_pkg.__file__).parent
        
        for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
            if module_name.startswith('_'):
                continue
            
            try:
                module = importlib.import_module(
                    f".connectors.{module_name}", 
                    package=__package__.rsplit('.', 1)[0]  # "comics"
                )
                
                # Find connector class in module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) 
                        and issubclass(attr, BaseConnector) 
                        and attr is not BaseConnector
                    ):
                        connector = attr()
                        connector.init_browser(self._browser)
                        self._connectors[connector.name.lower()] = connector
                        
            except Exception as e:
                print(f"Warning: Failed to load connector {module_name}: {e}")


    def get_connector(
        self, 
        *, 
        name: Optional[str] = None, 
        url: Optional[str] = None, 
        raise_error: bool = False
    ) -> Optional[BaseConnector]:
        """
        Find a connector by name or by URL. Only one of ``name`` or ``url`` should be provided.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the connector (case-insensitive).

        url: Optional[:class:`str`]
            The URL to find a connector for.

        raise_error: :class:`bool`
            If True and using ``url``, raise :class:`ConnectorNotFoundError` if no connector is found. 
            Defaults to ``False``. Only applies when ``url`` is provided.

        Returns
        -------
        Optional[:class:`BaseConnector`]
            The connector if found, else None.

        Raises
        ------
        :class:`ValueError`
            If both ``name`` and ``url`` are provided, or neither is provided.

        :class:`ConnectorNotFoundError`
            If no connector is found for the URL and ``raise_error`` is True.
        """

        if (name is None) == (url is None):
            raise ValueError("Exactly one of `name` or `url` must be provided.")

        if name is not None:
            return self._connectors.get(name.lower())

        for connector in self._connectors.values():
            if connector.can_handle(url):
                return connector
            
        if raise_error:
            raise ConnectorNotFoundError(url)
        
        return None
        
    
    @property
    def connectors(self) -> List[BaseConnector]:
        """List all available connectors as (name, base_url) tuples"""

        return [
            (c.name, c.base_url) 
            for c in self._connectors.values()
        ]


    @property
    def count(self) -> int:
        """Number of loaded connectors"""
        return len(self._connectors)
