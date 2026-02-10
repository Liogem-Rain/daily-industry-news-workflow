from typing import List, Dict
from youtubesearchpython import VideosSearch
from src.crawlers.base import BaseCrawler
import logging

class YouTubeCrawler(BaseCrawler):
    """
    Crawls YouTube search results for 'trending' or specific industry keywords.
    Uses 'youtube-search-python' to fetch videos without an API key.
    """
    def __init__(self, name: str, query: str, limit: int = 5):
        super().__init__(name, query)  # We use query instead of source_url here
        self.query = query
        self.limit = limit

    def fetch_articles(self) -> List[Dict]:
        """
        Executes a YouTube search based on the query, returning the top 'limit' results.
        Note: The library doesn't strictly guarantee 'today's most viewed' without filtering,
        but default search relevance often brings up recent/popular content.
        """
        try:
            # Simple search returns videos. The library handles pagination if limit > 20, 
            # but for small limits, one call is enough.
            # We can also add 'news' or 'today' to the query string for better relevance.
            videos_search = VideosSearch(self.query, limit=self.limit)
            results_dict = videos_search.result()

            video_list = []
            
            if not results_dict or 'result' not in results_dict:
                self.logger.warning(f"No results found for YouTube query: {self.query}")
                return []

            for video in results_dict['result']:
                title = video.get('title', 'No Title')
                link = video.get('link', '#')
                published_time = video.get('publishedTime', 'Unknown Date')
                view_count = video.get('viewCount', {}).get('short', 'Unknown Views')
                channel_name = video.get('channel', {}).get('name', 'Unknown Channel')
                thumbnail = video.get('thumbnails', [{}])[0].get('url', '')

                # Creating a summary-like string for the report
                summary = f"Channel: {channel_name} | Views: {view_count} | Posted: {published_time}"

                article = {
                    "source": "YouTube",
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "date": published_time,
                    "thumbnail": thumbnail  # Optional, can be used in report if markdown supports images
                }
                video_list.append(article)

            return video_list

        except Exception as e:
            self.logger.error(f"Error searching YouTube for {self.name}: {e}")
            return []
