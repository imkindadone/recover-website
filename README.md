

# Wayback Machine Archiver

A Python script to download archived web pages from the Wayback Machine, preserving the original structure and content.

## Table of Contents
- [Project Overview](#project-overview)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Usage](#usage)
- [URL Preparation](#url-preparation)
- [Code Features](#code-features)
- [Browser Simulation](#browser-simulation)
- [Scripts](#scripts)
- [Output Structure](#output-structure)
- [Examples](#examples)
- [Contributing](#contributing)

## Project Overview

This project was developed to recover valuable Persian texts that had disappeared from the live website [raheaakhar.com](https://raheaakhar.com). The script efficiently downloads archived pages from the Wayback Machine, handles URL decoding, and maintains the original directory structure.

## Environment Setup

### Prerequisites
- Python 3.6 or higher
- Internet connection to access Wayback Machine

### Required Packages
```bash
pip install requests tqdm
```

### System Dependencies
- Linux/macOS/Windows (script is platform-independent)
- No additional system dependencies required

## Installation

1. Clone or download the repository:
```bash
git clone <repository-url>
cd wayback-archiver
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command
```bash
python wayback_archiver.py urls.json
```

### Command Line Options
```bash
usage: wayback_archiver.py [-h] [--output OUTPUT] [--limit LIMIT] [--delay DELAY] input_file

Download archived pages from Wayback Machine using requests

positional arguments:
  input_file             Input JSON file containing URLs

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Output directory (default: archived_pages)
  --limit LIMIT         Limit number of pages to download
  --delay DELAY         Delay between requests in seconds (default: 1.0)
```

## URL Preparation

The script expects a JSON file with the following format:

```json
[
    ["original", "timestamp", "endkey"],
    ["https://raheaakhar.com/texts/page1", "20250124201322", "20250124201322"],
    ["https://raheaakhar.com/texts/page2", "20250124201322", "20250124201322"],
    ...
]
```

### Getting CDX Data from Wayback Machine

1. Use the Wayback Machine CDX API to get archived URLs:
```bash
curl "http://web.archive.org/cdx/search/cdx?url=raheaakhar.com/texts/*&output=json&fl=original,timestamp,endkey&from=20250124201322&to=20250124201322" > urls.json
```

2. **Note**: The raw CDX output needs to be converted to the format above. Use the provided conversion script.

## Code Features

1. **Efficient Downloading**:
   - Uses requests library for HTTP requests
   - Configurable delay between requests (default: 1 second)
   - 30-second timeout for unresponsive servers

2. **Directory Management**:
   - Creates output directory if it doesn't exist
   - Maintains original URL structure as subdirectories
   - Safe filename generation (replaces slashes with underscores)

3. **Error Handling**:
   - Comprehensive logging of errors and successes
   - Graceful handling of failed downloads
   - Detailed error messages for debugging

4. **Progress Tracking**:
   - Visual progress bar with tqdm
   - Detailed logging of each download

5. **Flexible Configuration**:
   - Command-line arguments for customization
   - Configurable output directory, delay, and download limit

## Browser Simulation

The script uses the following headers to mimic a Firefox browser request:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv=142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0, i"
}
```

These headers make the script appear as a real Firefox browser to the server, reducing the chance of being blocked or receiving simplified HTML.

## Scripts

### Main Script: `wayback_archiver.py`

```python
import os
import json
import time
import argparse
import logging
import requests
from urllib.parse import urlparse, unquote
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_page(wayback_url, output_dir, headers):
    """Download a page using requests"""
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract original URL from wayback URL
        # Wayback URL format: https://web.archive.org/web/{timestamp}/{original_url}
        original_url = wayback_url.split('/')[5]
        original_url = unquote(original_url)  # Decode URL-encoded characters
        
        # Extract path for filename
        parsed_url = urlparse(original_url)
        path = parsed_url.path
        if path.endswith('/'):
            path += 'index'
        
        # Clean filename
        filename = path.replace('/', '_').strip('_')
        
        # Save as HTML
        html_file = os.path.join(output_dir, f"{filename}.html")
        
        # Make request with headers
        logger.info(f"Downloading: {wayback_url}")
        response = requests.get(wayback_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save HTML content
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return html_file
    
    except Exception as e:
        logger.error(f"Error downloading {wayback_url}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Download archived pages from Wayback Machine using requests")
    parser.add_argument("input_file", help="Input JSON file containing URLs")
    parser.add_argument("--output", default="archived_pages", help="Output directory")
    parser.add_argument("--limit", type=int, help="Limit number of pages to download")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    
    args = parser.parse_args()
    
    # Headers to mimic the fetch request
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv=142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0, i"
    }
    
    # Read input file
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return
    
    # Skip the header row
    if data and data[0] == ["original", "timestamp", "endkey"]:
        url_data = data[1:]
    else:
        url_data = data
    
    # Convert to wayback URLs
    wayback_urls = []
    for entry in url_data:
        if len(entry) >= 2:
            original_url = entry[0]
            timestamp = entry[1]
            wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
            wayback_urls.append({
                "original_url": original_url,
                "wayback_url": wayback_url
            })
    
    if not wayback_urls:
        logger.error("No valid URLs found in input file")
        return
    
    logger.info(f"Found {len(wayback_urls)} URLs to download")
    
    # Limit if specified
    if args.limit and args.limit < len(wayback_urls):
        wayback_urls = wayback_urls[:args.limit]
        logger.info(f"Limited to {args.limit} URLs")
    
    # Download each page
    logger.info(f"Downloading pages to {args.output}...")
    for url_info in tqdm(wayback_urls, desc="Downloading"):
        original_url = url_info["original_url"]
        wayback_url = url_info["wayback_url"]
        
        # Create subdirectory based on original URL path
        parsed = urlparse(original_url)
        path_dir = os.path.join(args.output, parsed.path.lstrip('/').replace('/', '_'))
        
        html_file = download_page(wayback_url, path_dir, headers)
        
        if html_file:
            logger.info(f"Saved: {html_file}")
        
        # Respect rate limits
        time.sleep(args.delay)
    
    logger.info("All downloads completed")

if __name__ == "__main__":
    main()
```

### URL Conversion Script: `convert_urls.py`

```python
import json
import sys

def convert_cdx_to_wayback_urls(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        wayback_urls = []
        for entry in data[1:]:  # Skip header row
            if len(entry) >= 2 and entry[0] and entry[1]:
                original_url = entry[0]
                timestamp = entry[1]
                wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                wayback_urls.append({
                    "original_url": original_url,
                    "wayback_url": wayback_url
                })
        
        with open(output_file, 'w') as f:
            json.dump(wayback_urls, f, indent=2)
        
        print(f"Converted {len(wayback_urls)} URLs to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_urls.py input.json output.json")
        sys.exit(1)
    
    convert_cdx_to_wayback_urls(sys.argv[1], sys.argv[2])
```

## Output Structure

The script creates a directory structure that mirrors the original website:

```
archived_pages/
├── texts/
│   ├── مقاض_اضطرار_شش_جلسه/
│   │   └── مقاض_اضطرار_شش_جلسه.html
│   ├── page1/
│   │   └── page1.html
│   └── page2/
│       └── page2.html
```

Each page is saved as an HTML file in a subdirectory matching its original path, with special characters handled appropriately.

## Examples

### Basic Usage
```bash
python wayback_archiver.py urls.json
```

### With Custom Output Directory
```bash
python wayback_archiver.py urls.json --output my_archive
```

### With Custom Delay
```bash
python wayback_archiver.py urls.json --delay 2.0
```

### With Download Limit
```bash
python wayback_archiver.py urls.json --limit 100
```

## Contributing

Contributions are welcome! If you find a bug or have a suggestion, please open an issue or submit a pull request.

### Steps to Contribute
1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

---

*Created to preserve valuable digital content from the Wayback Machine*
