from typing import List, Dict, Optional
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from src.crawlers.base import BaseCrawler
import logging
import re

class YouTubeCrawler(BaseCrawler):
    """
    Crawls YouTube search results and attempts to fetch transcripts for summarization.
    """
    def __init__(self, name: str, query: str, limit: int = 5, fetch_transcript: bool = True):
        super().__init__(name, query) 
        self.query = query
        self.limit = limit
        self.fetch_transcript = fetch_transcript

    def _get_video_id(self, url: str) -> Optional[str]:
        """Extracts video ID from URL."""
        # Simple regex for standard youtube URLs
        match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
        # Handle short URLs like youtu.be/ID
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
        return None

    def _get_transcript_text(self, video_id: str) -> str:
        """Fetches transcript text for a video ID."""
        try:
            # Try to get English or auto-generated English, or fall back to any available
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Prefer English, then manual, then auto-generated
            try:
                transcript = transcript_list.find_transcript(['en', 'zh-Hans'])
            except:
                # Fallback to any available if specific language not found
                # Or translate able transcript
                 target_language = 'en'
                 try:
                     transcript = transcript_list.find_generated_transcript(['en'])
                 except: 
                     # iter and take first
                     for t in transcript_list:
                         transcript = t
                         break

            formatter = TextFormatter()
            text = formatter.format_transcript(transcript.fetch())
            return text
        except Exception as e:
            self.logger.warning(f"Could not fetch transcript for {video_id}: {e}")
            return ""

    def fetch_articles(self) -> List[Dict]:
        """
        Executes a YouTube search based on the query, providing video details and raw transcript text if available.
        """
        try:
            # Add 'news' to query if not present to bias towards news content
            full_query = f"{self.query} news" if "news" not in self.query.lower() else self.query
            
            videos_search = VideosSearch(full_query, limit=self.limit)
            results_dict = videos_search.result()

            video_list = []
            
            if not results_dict or 'result' not in results_dict:
                self.logger.warning(f"No results found for YouTube query: {self.query}")
                return []

            for video in results_dict['result']:
                title = video.get('title', 'No Title')
                link = video.get('link', '#')
                published_time = video.get('publishedTime', 'Unknown Date')
                view_count = video.get('viewCount', {}).get('short', '0')
                channel_name = video.get('channel', {}).get('name', 'Unknown Channel')
                
                video_id = video.get('id', self._get_video_id(link))
                
                transcript_text = ""
                if self.fetch_transcript and video_id:
                    transcript_text = self._get_transcript_text(video_id)
                    # Limit transcript length to avoid context window explosion (e.g. first 5000 chars)
                    transcript_text = transcript_text[:8000] 

                article = {
                    "source": "YouTube",
                    "title": title,
                    "url": link,
                    "video_id": video_id,
                    "channel": channel_name,
                    "views": view_count,
                    "date": published_time,
                    "transcript": transcript_text, # Raw text for LLM to summarize
                    "has_transcript": bool(transcript_text)
                }
                video_list.append(article)

            return video_list

        except Exception as e:
            self.logger.error(f"Error searching YouTube for {self.name}: {e}")
            return []
