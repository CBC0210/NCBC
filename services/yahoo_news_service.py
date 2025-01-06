import os
import json
import requests
from bs4 import BeautifulSoup

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")

YAHOO_NEWS_URL = "https://tw.news.yahoo.com"  # Yahoo奇摩新聞首頁

def fetch_yahoo_news_and_save():
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
        all_news.append({
            "title": title,
            "link": link,
            "published": hot_data["published"],
            "content": hot_data["content"]
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

        news_item = {
            "title": title,
            "link": link,
            "published": published_time,
            "content": content_text
        }
        all_news.append(news_item)

    # 4) 輸出 JSON
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(TEMP_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    return all_news

def fetch_article_content(url: str) -> dict:
    """
    給定新聞連結，嘗試以 requests + BeautifulSoup 爬取內文。
    回傳一個包含 'published' 與 'content' 的字典 (如抓不到則給預設值)。
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.82 Safari/537.36"
        }
        resp = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 簡單示範：抓 <p> 文字 (實際要視該新聞頁的 HTML 結構)
        paragraphs = soup.find_all("p")
        content_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # 嘗試抓取時間
        time_tag = soup.find("time", class_="caas-attr-meta-time")
        published_time = time_tag.get_text(strip=True) if time_tag else "無發布時間"

        print(f"抓取內文成功: {url}")
        # 只取前 1000 字，避免過長
        return {
            "published": published_time,
            "content": content_text[:1000]
        }

    except Exception as e:
        print(f"抓取內文失敗: {url}, 錯誤: {e}")
        return {
            "published": "無發布時間",
            "content": ""
        }
    except Exception as e:
        print(f"抓取內文失敗: {url}, 錯誤: {e}")
        return ""
