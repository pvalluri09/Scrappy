import asyncio
import httpx
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import re
import concurrent.futures

from db import get_client


# crawler - visits a base page, extracts all URLs and explore them recursively
# scraper - pulls the HTML content from a specific page


def crawl_page(url: str) -> list[str]:
    start = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    base_url = urlparse(url).hostname
    matches = []
    for match in soup.find_all("a"):
        try:
            if not re.match("(http[s]*://)", match["href"]):
                matches.append("https://" + base_url + match["href"])
        except Exception as e:
            print(f"Base URL: {url}, no HREF found for {match}")
    print("Matches", len(matches))
    print(matches)
    return matches


async def scrape_pages(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        page = await client.get(url, headers=headers)
        record = {
            "url": url,
            "content": page.content.strip(),
            "timestamp": datetime.now(),
        }
    return record


def scrape_pages_threaded(urls: list[str]):
    records = []
    for url in urls:
        content = scrape_page(url)
        records.append(content)
    return records


def scrape_page(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
    }
    page = requests.get(url, headers=headers)
    record = {"url": url, "content": page.content, "timestamp": datetime.now()}
    return record

async def scrape_pages_async_thread(url: str) -> dict:
    async def fetch_content(url: str) -> bytes:
        # Define a blocking or CPU-bound task (e.g., fetching content with requests)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
        }
        response = requests.get(url, headers=headers)
        return response.content

    content = await asyncio.to_thread(fetch_content, url)

    record = {
        "url": url,
        "content": content.strip(),
        "timestamp": datetime.now(),
    }
    return record