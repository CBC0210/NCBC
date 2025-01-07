import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_article_content(url: str) -> dict:
    """
    給定新聞連結，嘗試以 requests + BeautifulSoup 爬取內文與圖片。
    回傳一個包含 'published', 'content' 與 'images' 的字典 (如抓不到則給預設值)。
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
        published_time = time_tag.get_text(strip=True) if time_tag else "no time"
        if published_time == "no time":
            time_tag = soup.find("time")
            published_time = time_tag["datetime"] if time_tag else "no time"
        if published_time != "no time":
            try:
                dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%SZ")
                published_time = dt.strftime("%Y年%m月%d日 %p%I:%M").replace("AM", "上午").replace("PM", "下午")
            except ValueError:
                pass
        

        # 嘗試抓取圖片
        images = []
        meta_tags = soup.find_all("meta", {"property": "og:image"})
        for meta in meta_tags:
            image_url = meta.get("content")
            if image_url and not image_url.endswith(".ico"):
                images.append(image_url)

        print(f"抓取內文成功: {url}")
        # 只取前 1000 字，避免過長
        return {
            "published": published_time,
            "content": content_text[:1000],
            "images": images
        }

    except Exception as e:
        print(f"抓取內文失敗: {url}, 錯誤: {e}")
        return {
            "published": "無發布時間",
            "content": "",
            "images": []
        }