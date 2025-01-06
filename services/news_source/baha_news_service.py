import os
import json
from typing import Dict
import requests
from bs4 import BeautifulSoup
from services.news_source.fetch_article_content import fetch_article_content

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")

BAHA_NEWS_URL = "https://gnn.gamer.com.tw/"  # 巴哈姆特新聞首頁

def fetch_baha_news():
    """
    1) 從 巴哈姆特新聞首頁抓取 HTML
    2) 解析新聞標題與連結
    3) 針對每個連結，再進一步嘗試抓內文
    4) 最後將結果輸出到 data/temp_news.json
    """

    all_news = []

    # 1) 取得 巴哈姆特新聞首頁的 HTML
    try:
        resp = requests.get(BAHA_NEWS_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"無法取得 巴哈姆特新聞首頁: {e}")
        return

    # 2) 解析 HTML，找出新聞列表
    soup = BeautifulSoup(resp.text, "html.parser")
    news_items = soup.select("div.GN-lbox2B")

    for news_item in news_items:
        title_tag = news_item.select_one("h1.GN-lbox2D a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag["href"].strip()
        if not link.startswith("https://"):
            link = "https:" + link

        # 3) 嘗試抓取內文
        article_data = fetch_article_content(link)
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

def fetch_article_content(url: str) -> Dict[str, str]:
    """
    從指定的 URL 抓取新聞內文、發佈時間和圖片。
    
    Args:
        url (str): 新聞文章的 URL。
    
    Returns:
        Dict[str, str]: 包含內文、發佈時間和圖片的字典。
    """
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"無法取得文章內容: {e}")
        return {"published": "", "content": "", "images": []}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract the JSON-LD script
    json_ld_script = soup.find("script", type="application/ld+json")
    if json_ld_script:
        json_ld_data = json.loads(json_ld_script.string)
        if isinstance(json_ld_data, list):
            json_ld_data = json_ld_data[0]
        published_time = json_ld_data.get("datePublished", "")
    else:
        published_time = ""

    content_text = ""
    content_div = soup.find("div", class_="GN-lbox3B")
    if content_div:
        content_text = content_div.get_text(strip=True)

    images = []
    image_tags = soup.select("div.GN-lbox3C img")
    for img in image_tags:
        img_url = img["src"]
        if not img_url.startswith("https://"):
            img_url = "https:" + img_url
        images.append(img_url)

    return {"published": published_time, "content": content_text, "images": images}

