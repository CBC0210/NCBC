import os
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
from googlenewsdecoder import new_decoderv1

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")

GOOGLE_NEWS_RSS = [
    # 台灣版
    "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    # 全球版
    # "https://news.google.com/rss",
]

def fetch_google_news_and_save(limit_per_feed=5):
    """
    從「Google 新聞台灣版」與「全球版」RSS 抓取最新新聞，
    逐一進入其連結爬取內文，最後將結果輸出到 data/temp_news.json

    limit_per_feed: 每個 RSS 限制抓取幾則新聞 (避免測試時量太大)
    """
    all_news = []

    for rss_url in GOOGLE_NEWS_RSS:
        print(f"解析 RSS: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            # bozo=True 表示 RSS 解析可能有錯誤
            print(f"RSS 解析錯誤: {feed.bozo_exception}")
            continue

        entries = feed.entries[:limit_per_feed]

        for entry in entries:
            title = entry.title
            link = entry.link
            link = extract_original_url(link)
            print(f"抓取新聞: {title} ({link})")
            published = getattr(entry, 'published', '無發布時間')  # 有些 RSS 可能沒 published
            
            # 嘗試爬取新聞原文
            
            content_text = fetch_article_content(link)

            news_item = {
                "title": title,
                "link": link,
                "published": published,
                "content": content_text
            }
            all_news.append(news_item)
    
    # 將最終結果輸出到 data/temp_news.json
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(TEMP_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

    print(f"已抓取 {len(all_news)} 則新聞，存檔於 {TEMP_NEWS_FILE}")

def extract_original_url(google_url: str) -> str:
    """
    Extract the original URL from a Google News link.
    """
    try:
        interval_time = 10 # default interval is 1 sec, if not specified
        decoded_url = new_decoderv1(google_url, interval=interval_time)
        if decoded_url.get("status"):
            print("Decoded URL:", decoded_url["decoded_url"])
            return decoded_url["decoded_url"]
        else:
            print("Error:", decoded_url["message"])
            return google_url
    except Exception as e:
        print(f"Error occurred: {e}")
        return google_url

def fetch_article_content(url: str) -> str:
    """
    給定新聞連結，嘗試以 requests + BeautifulSoup 爬取內文。
    回傳抓到的文字 (如抓不到，回傳空字串)。
    """
    try:
        headers = {
            # 有些網站可能需要基本的瀏覽器標頭，避免被擋
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.82 Safari/537.36"
        }
        resp = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 這裡只是範例，實際每家媒體網頁結構不同
        # 以下只是嘗試抓 <p> 文字
        paragraphs = soup.find_all("p")
        content_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # 如果想做更進階的清理，可再用正則或篩選器剔除廣告/標籤
        print(f"抓取內文: {url}")
        return content_text[:1000]  # 範例：只取前 1000 字，避免太長
    except Exception as e:
        print(f"抓取內文失敗: {url}, 錯誤: {e}")
        return ""

