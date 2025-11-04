import os
import requests
import time
import feedparser
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BACKEND_API_URL = "http://localhost:5000/api/process-text"

def process_item(headline, description="", url=""):
    """Sends a news item to the backend for processing."""
    if not headline or headline == "[Removed]" or not url:
        return

    print(f"\nProcessing: '{headline}'")
    full_text = f"{headline}. {description or ''}"

    # --- UPDATED: Add the 'url' to the payload ---
    payload = {"text": full_text, "url": url}

    try:
        requests.post(BACKEND_API_URL, json=payload, timeout=15) # Increased timeout slightly
        print("-> Sent to backend.")
    except requests.exceptions.RequestException as e:
        print(f"-> Error contacting backend: {e}")

def fetch_from_news_api():
    print("\n--- Fetching from NewsAPI (India) ---")
    keywords = "(flood OR earthquake OR landslide OR accident OR traffic OR tsunami OR cyclone OR storm OR heavy rain) AND India"
    api_url = (f"https://newsapi.org/v2/everything?qInTitle={requests.utils.quote(keywords)}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        print(f"Found {len(articles)} articles from NewsAPI.")
        for article in articles:
            process_item(article['title'], article.get('description'), article.get('url'))
            time.sleep(2)
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")

def fetch_from_rss(feed_url):
    print(f"\n--- Fetching from RSS Feed: {feed_url} ---")
    try:
        feed = feedparser.parse(feed_url)
        print(f"Found {len(feed.entries)} items in feed.")
        for entry in feed.entries:
            process_item(entry.title, entry.get('summary'), entry.get('link'))
            time.sleep(2)
    except Exception as e:
        print(f"Error fetching from RSS feed: {e}")

if __name__ == "__main__":
    rss_feeds = [
        "https://timesofindia.indiatimes.com/rssfeeds/3942321.cms", 
        "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss"
    ]

    fetch_from_news_api()
    for feed in rss_feeds:
        fetch_from_rss(feed)

    print("\n--- All sources checked. ---")