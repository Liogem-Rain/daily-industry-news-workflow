from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import feedparser

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

class BaseCrawler(ABC):
    def __init__(self, name: str, source_url: str):
        self.name = name
        self.source_url = source_url
        self.logger = logging.getLogger(name)

    @abstractmethod
    def fetch_articles(self) -> List[Dict]:
        """Fetch and parse articles, returning a list of dicts with title, url, summary, date."""
        pass

    def run(self) -> List[Dict]:
        """Main execution method."""
        try:
            self.logger.info(f"Starting crawl for {self.name}...")
            articles = self.fetch_articles()
            self.logger.info(f"Found {len(articles)} articles from {self.name}.")
            return articles
        except Exception as e:
            self.logger.error(f"Failed to crawl {self.name}: {e}")
            return []

class RSSCrawler(BaseCrawler):
    """Generic Crawler for any RSS Feed source."""
    
    def fetch_articles(self) -> List[Dict]:
        feed = feedparser.parse(self.source_url)
        results = []
        # Get top 10 entries
        for entry in feed.entries[:10]:
            article = {
                "source": self.name,
                "title": entry.title,
                "url": entry.link,
                "summary": getattr(entry, "summary", getattr(entry, "description", "")),
                "date": getattr(entry, "published", getattr(entry, "updated", "Unknown Date"))
            }
            results.append(article)
        return results

class HTMLCrawler(BaseCrawler):
    """Base class for custom HTML scraping."""
    
    def get_soup(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(self.source_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, 'lxml')
