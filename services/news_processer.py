import os
import json
from typing import List, Dict
from services.news_service import get_latest_news
from utils.json_utils import load_json, save_json
from datetime import datetime, timedelta
from config.config import NEWS_MEMORY
from services.openai_gpt_processing_service import clean_content, generate_new_title, generate_new_content, generate_summary_as_critic
from services.forum_post_service import process_forum_posts
import asyncio

DATA_FOLDER = "data"
TEMP_NEWS_FILE = os.path.join(DATA_FOLDER, "temp_news.json")
YAHOO_NEWS_URL = "https://tw.news.yahoo.com"  # Yahoo奇摩新聞首頁

async def process_yahoo_news(bot):
    """
    抓取 Yahoo奇摩新聞並進行後續處理。
    包含：
    - 抓取新聞標題與連結
    - 抓取每則新聞的內文
    - 儲存結果到 JSON 檔案
    - 返回處理後的新聞資料清單
    [
        {
            "title": "標題",
            "link": "鏈接",
            "published": "%y年%m月%d日 %p%I:%M",
            "content": "内容",
            "images": []
        },
    ]
    """
    all_news = await asyncio.to_thread(get_latest_news)
    # Load existing news memory
    news_memory_file = os.path.join(DATA_FOLDER, "news_memory.json")
    news_memory = await asyncio.to_thread(load_json, news_memory_file)
    if not isinstance(news_memory, list):
        news_memory = []
    # Filter out news that are already in memory
    filtered_news = [news for news in all_news if news["title"] not in {n["title"] for n in news_memory}]
    # Update news memory with new news
    news_memory.extend(filtered_news)
    # Update all_news to only include filtered news
    all_news = filtered_news

    # Remove news older than retention period from memory
    # Define the retention period (5 days)
    retention_period = timedelta(days=NEWS_MEMORY)
    current_time = datetime.now()

    ### 這裡的程式碼需要修改，應該要使用try，然後嘗試不同格式的解析方式，如果全部不行則寫入目前時間 ###
    def parse_published_date(date_str):
        date_str = date_str.replace("下午", "PM").replace("上午", "AM")
        formats = ["%Y年%m月%d日 %p%I:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # If all formats fail, return current time
        return datetime.now()
    
    news_memory = [news for news in news_memory if parse_published_date(news["published"]) >= current_time - retention_period]
    # Save the filtered news memory
    await asyncio.to_thread(save_json, news_memory_file, news_memory)

    for item in all_news:
        item['content'] = await asyncio.to_thread(clean_content, item['content'])
        item['title'] = await asyncio.to_thread(generate_new_title, item['title'], item['content'])
        item['content'] = await asyncio.to_thread(generate_new_content, item['content'])
        item['comment'] = await asyncio.to_thread(generate_summary_as_critic, item['title'], item['content'])
        print()

    await process_forum_posts(all_news, bot)

# 可選：定義後續處理函式，例如發送到 Discord 頻道
# def send_to_discord(news: Dict[str, str]):
#     # 實作發送消息到特定 Discord 頻道的邏輯
#     pass