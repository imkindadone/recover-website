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
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
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
