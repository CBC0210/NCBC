import os
import json
from typing import Dict
import requests
from bs4 import BeautifulSoup
from services.news_source.fetch_article_content import fetch_article_content

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")

GAMER_NEWS_URL = "https://www.4gamers.com.tw/news"  # 4Gamers新聞首頁

def fetch_gamer_news():
    """
    1) 從 4Gamers新聞首頁抓取 HTML
    2) 解析新聞標題與連結
    3) 針對每個連結，再進一步嘗試抓內文
    4) 最後將結果輸出到 data/temp_news.json
    """

    all_news = []

    # 1) 取得 4Gamers新聞首頁的 HTML
    try:
        resp = requests.get(GAMER_NEWS_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"無法取得 4Gamers新聞首頁: {e}")
        return

    # 2) 解析 HTML，找出新聞列表
    soup = BeautifulSoup(resp.text, "html.parser")
    news_items = soup.select("div h4 a")
    # Load existing news memory
    news_memory_file = os.path.join(DATA_FOLDER, "news_memory.json")
    try:
        with open(news_memory_file, "r", encoding="utf-8") as f:
            news_memory = json.load(f)
    except FileNotFoundError:
        news_memory = []

    if not isinstance(news_memory, list):
        news_memory = []

    existing_titles = {news["title"] for news in news_memory}

    for news_item in news_items:
        title = news_item.get_text(strip=True)
        # Filter out news that are already in memory
        if title in existing_titles:
            continue
        link = news_item["href"].strip()
        if not link.startswith("https://"):
            link = "https://www.4gamers.com.tw" + link

        # 3) 嘗試抓取內文
        article_data = fetch_article_content(link)
        if article_data["content"] == "":
            continue
        published_time = article_data["published"]
        content_text = article_data["content"]
        images = article_data["images"]

        news_item = {
            "title": title,
            "link": link,
            "published": published_time,
            "content": content_text,
            "images": images
        }
        all_news.append(news_item)

    # 4) 輸出 JSON
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(TEMP_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    return all_news

