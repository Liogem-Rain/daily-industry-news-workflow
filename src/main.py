import yaml
import schedule
import time
import os
import datetime
from typing import List, Dict
from src.crawlers.base import RSSCrawler, BaseCrawler
from src.crawlers.youtube import YouTubeCrawler
from src.summary import NewsSummarizer
from dotenv import load_dotenv

# Load environment variables (e.g., from .env file for local dev)
load_dotenv()

def load_config(config_path="config.yaml"):
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def run_crawlers(sources: List[Dict]) -> List[Dict]:
    results = []
    print(f"[{datetime.datetime.now()}] Starting news crawl...")
    
    if not sources:
        print("No sources configured.")
        return results

    for source_conf in sources:
        crawl_type = source_conf.get('type')
        name = source_conf.get('name')
        category = source_conf.get('category', 'General')
        limit = source_conf.get('limit', 10) # Default to 10

        try:
            if crawl_type == 'youtube':
                query = source_conf.get('query')
                # Fetch transcripts for better summarization
                crawler = YouTubeCrawler(name, query, limit=limit, fetch_transcript=True)
                videos = crawler.fetch_articles()
                for v in videos:
                    v['category'] = category
                results.extend(videos)
            
            else:
                # Keep RSS fallback logic if needed
                url = source_conf.get('url')
                crawler = RSSCrawler(name, url)
                articles = crawler.run()
                for a in articles:
                    a['category'] = category
                results.extend(articles)
                
        except Exception as e:
            print(f"Crawler failed for {name}: {e}")
            
    return results


def generate_report(articles: List[Dict], output_conf: Dict):
    report_path = output_conf.get('path', 'daily_news_summary.md')
    
    # Initialize Summarizer
    summarizer = NewsSummarizer()
    
    # Group by category manually for processing
    grouped_articles = {}
    for article in articles:
        cat = article.get('category', 'General')
        if cat not in grouped_articles:
            grouped_articles[cat] = []
        grouped_articles[cat].append(article)
    
    content = f"# 每日行业热点总结\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Define category order if possible from config (need to pass config down later, but simple sort works for now)
    # Or just iterate gathered categories
    
    for cat, items in grouped_articles.items():
        print(f"Summarizing category: {cat} with {len(items)} items...")
        summary_text = summarizer.summarize_category(cat, items)
        
        content += f"## {cat}\n"
        content += f"{summary_text}\n\n"
        
    with open(report_path, 'w') as f:
        f.write(content)
        
    print(f"Report generated: {report_path}")

def job():
    config = load_config()
    articles = run_crawlers(config['sources'])
    generate_report(articles, config['output'])
    print("Job completed successfully.")

if __name__ == "__main__":
    # Always run once immediately
    job()
    
    # If running in CI/CD environment (e.g. GitHub Actions), exit after one run
    if os.getenv('CI'):
        print("Running in CI environment. Exiting after single execution.")
        exit(0)
    
    # Otherwise, schedule to run every day at 08:00 AM
    schedule.every().day.at("08:00").do(job)
    
    print("Scheduler started. Running daily at 08:00. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(60)
