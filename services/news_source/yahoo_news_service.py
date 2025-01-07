import os
import json
import requests
from bs4 import BeautifulSoup
from services.news_source.fetch_article_content import fetch_article_content

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")

YAHOO_NEWS_URL = "https://tw.news.yahoo.com"  # Yahoo奇摩新聞首頁

def fetch_yahoo_news():
    """
    1) 從 Yahoo奇摩新聞首頁抓取 HTML
    2) 解析新聞標題與連結
    3) 針對每個連結，再進一步嘗試抓內文
    4) 最後將結果輸出到 data/temp_news.json
    """

    all_news = []

    # 1) 取得 Yahoo 新聞首頁的 HTML
    try:
        resp = requests.get(YAHOO_NEWS_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"無法取得 Yahoo新聞首頁: {e}")
        return

    # 2) 解析 HTML，找出新聞列表
    soup = BeautifulSoup(resp.text, "html.parser")
    hot_tags = soup.select("li._yb_1y70zwh._yb_su6olx a")
    for a_tag in hot_tags:
        title_div = a_tag.find("div", class_="_yb_3cjtcc")
        title = title_div.get_text(strip=True) if title_div else None
        if not title:
            continue
        link = a_tag["href"].strip()
        if link.startswith("/"):
            link = YAHOO_NEWS_URL + link
        hot_data = fetch_article_content(link)
        if hot_data["content"] == "":
            continue
        all_news.append({
            "title": title,
            "link": link,
            "published": hot_data["published"],
            "content": hot_data["content"],
            "images": hot_data["images"]
        })

    # 這裡根據你提供的原始碼，新聞似乎出現在 <li class="Pos(r) Lh(1.5) H(24px) Mb(8px)"> 裡
    # 你可視需要擴大/縮小範圍，或使用其他選擇器
    li_tags = soup.select("li.Pos\\(r\\).Lh\\(1\\.5\\).H\\(24px\\).Mb\\(8px\\)")

    # 3) 逐一擷取 <a> 標籤內的標題、連結
    for li in li_tags:
        a_tag = li.find("a", href=True)
        if not a_tag:
            continue

        title = a_tag.get_text(strip=True)
        link = a_tag["href"].strip()

        # 若連結是相對路徑，補上 https://tw.news.yahoo.com
        if link.startswith("/"):
            link = YAHOO_NEWS_URL + link

        # 嘗試抓取內文
        content_text = fetch_article_content(link)

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

