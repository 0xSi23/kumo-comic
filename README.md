# KumoComic

A HakuNeko-inspired manga/comic downloader with connector-based architecture.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Connector-based architecture**: Each website has its own connector module.
- **Stealth mode**: Uses playwright-stealth and random User-Agent rotation.
- **Rate limiting**: Configurable delays to avoid being blocked.
- **Batch download**: Download all chapters from a comic page.
- **Beautiful CLI (Not yet)**: Rich progress bars and formatted output.

## Supported Websites

| Website | Status |
|---------|--------|
| TruyenQQ | ✅ Working |

## Installation

```bash
pip install kumo-comic
playwright install chromium
```

## Usage

<!-- ### Command Line

```bash
# Download single chapter
kumocomic "https://truyenqqno.com/truyen-tranh/one-piece-245-chap-1.html"

# Download ALL chapters from manga page
kumocomic "https://truyenqqno.com/truyen-tranh/one-piece-245" --all

# Show browser window (for debugging)
kumocomic "https://example.com/manga/chapter" --visible

# Interactive mode
kumocomic
```

### Python API

```python
import asyncio
from kumocomic import download_chapter, download_manga

# Download single chapter
asyncio.run(download_chapter("https://example.com/manga/chapter-1"))

# Download all chapters
asyncio.run(download_manga("https://example.com/manga"))
``` -->

### Custom Connector

```python
from kumocomic import BaseConnector, Manga, Chapter

class MyConnector(BaseConnector):
    name = "MySite"
    domains = ["mysite.com"]
    
    async def get_manga_info(self, url: str) -> Manga:
        # Implementation
        pass
    
    async def get_chapter_images(self, chapter: Chapter) -> list[str]:
        # Implementation
        pass
```

## Development

```bash
git clone https://github.com/0xSi23/kumo-comic
cd kumocomic
pip install -e ".[dev]"
playwright install chromium
```

## License

MIT License - see [LICENSE](LICENSE) file.
