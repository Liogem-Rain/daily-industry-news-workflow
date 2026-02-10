import yaml
import schedule
import time
import os
import datetime
from typing import List, Dict
from src.crawlers.base import RSSCrawler, BaseCrawler
from src.crawlers.youtube import YouTubeCrawler # Import the new crawler

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
        limit = source_conf.get('limit', 5)

        try:
            if crawl_type == 'rss':
                url = source_conf.get('url')
                crawler = RSSCrawler(name, url)
                articles = crawler.run()
                for a in articles:
                    a['category'] = category
                results.extend(articles)
            
            elif crawl_type == 'youtube':
                query = source_conf.get('query')
                crawler = YouTubeCrawler(name, query, limit=limit)
                videos = crawler.run()
                for v in videos:
                    v['category'] = category
                    v['is_video'] = True
                results.extend(videos)
                
            else:
                print(f"Unknown crawler type: {crawl_type} for {name}")
                
        except Exception as e:
            print(f"Crawler failed for {name}: {e}")
            
    return results

def generate_report(articles: List[Dict], output_conf: Dict):
    report_format = output_conf.get('format', 'markdown')
    report_path = output_conf.get('path', 'daily_news_report.md')
    
    # Sort by category then date
    articles.sort(key=lambda x: (x.get('category', ''), x.get('date', '')))
    
    content = f"# Daily Industry News Report\nGenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Group by category manually for cleaner output
    grouped_articles = {}
    for article in articles:
        cat = article.get('category', 'General')
        if cat not in grouped_articles:
            grouped_articles[cat] = []
        grouped_articles[cat].append(article)

    for cat, items in grouped_articles.items():
        content += f"## {cat}\n\n"
        for idx, article in enumerate(items, 1):
            title = article.get('title', 'No Title')
            url = article.get('url', '#')
            summary = article.get('summary', '')
            thumbnail = article.get('thumbnail')
            
            content += f"### {idx}. [{title}]({url})\n"
            if thumbnail:
                content += f"[![Thumbnail]({thumbnail})]({url})\n"
            content += f"**Details**: {summary}\n\n"
        content += "---\n"
        
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
