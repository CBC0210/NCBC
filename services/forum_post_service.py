# services/forum_post_service.py
import os
import json
from typing import List, Dict
import discord
import asyncio
from datetime import datetime, timedelta, timezone

from config.config import NEWS_MEMORY,DATA_FOLDER, FORUM_CHANNELS_FILE, SIMILARITY_THRESHOLD
from services.openai_embed_service import get_text_embedding, compare_embeddings
from services.openai_gpt_processing_service import determine_tags

# 定義東八區的時區
tz_utc_plus_8 = timezone(timedelta(hours=8))

async def get_since(days: int):
    now = datetime.now(tz_utc_plus_8)
    since = now - timedelta(days=days)
    return since

def load_forum_channels() -> List[int]:
    """
    從 forum_channels.json 讀取所有論壇頻道的 Channel ID。
    
    Returns:
        List[int]: 所有論壇頻道的 ID 列表。
    """
    if not os.path.exists(FORUM_CHANNELS_FILE):
        print(f"論壇頻道檔案不存在: {FORUM_CHANNELS_FILE}")
        return []
    
    with open(FORUM_CHANNELS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # 提取所有 Channel IDs
            channel_ids = []
            for guild_id, channels in data.items():
                channel_ids.extend(channels)
            return channel_ids
        except json.JSONDecodeError as e:
            print(f"讀取論壇頻道檔案時發生錯誤: {e}")
            return []

async def fetch_recent_posts(bot, channel_id: int, days: int = NEWS_MEMORY) -> List[discord.Message]:
    """
    從指定的 Discord 頻道抓取過去指定天數內的所有貼文。
    
    Args:
        bot (discord.Bot): Discord Bot 實例。
        channel_id (int): 目標頻道的 ID。
        days (int, optional): 多少天內的貼文。預設為 5 天。
    
    Returns:
        List[discord.Message]: 過去指定天數內的貼文列表。
    """
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"無法找到頻道 ID: {channel_id}")
        return []
    
    since = (await get_since(days))
    posts = []
    threads = channel.threads  # Remove the parentheses to access the list of threads
    for thread in threads:
        last_message_time = thread.last_message.created_at if thread.last_message else thread.created_at
        if thread.archived or (len(thread.members) <= 1 and (datetime.now(tz_utc_plus_8) - last_message_time).days > 1):
            await thread.delete()
        else:
            posts.append(thread)
    
    posts = posts[:100]
    print(f"已抓取頻道 {channel_id} 過去 {days} 天內的 {len(posts)} 則貼文。")
    return posts

async def process_forum_posts(all_news, bot, days: int = NEWS_MEMORY):
    """
    處理所有論壇頻道的貼文。
    包含：
    - 取得論壇頻道
    - 抓取過去指定天數的貼文
    - 判斷貼文標題和我們新的新聞標題的相似度，如果達到一定閾值（configable），則進行後續處理1，否則進行後續處理2
    - 後續處理1: 更新貼文、發佈新內容、更新標題
    - 後續處理2: 發佈新貼文
    
    Args:
        bot (discord.Bot): Discord Bot 實例。
        days (int, optional): 多少天內的貼文。預設為 5 天。
    """
    channel_ids = await asyncio.to_thread(load_forum_channels)
    if not channel_ids:
        print("沒有找到任何論壇頻道需要處理。")
        return
    

    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f"無法找到頻道 ID: {channel_id}")
            # 刪除 forum_channels.json 中的該頻道
            try:
                with open(FORUM_CHANNELS_FILE, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    for guild_id, channels in data.items():
                        if channel_id in channels:
                            channels.remove(channel_id)
                            break
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"已刪除 forum_channels.json 中的頻道 ID: {channel_id}")
            except Exception as e:
                print(f"刪除 forum_channels.json 中的頻道 ID 時發生錯誤: {e}")
            continue

        posts = await fetch_recent_posts(bot, channel_id, days)
        
        for post in posts:
            # 假設貼文的標題和內容在訊息的 embed 中
            original_title = post.name if post.name else "no title"
            embed_title = await asyncio.to_thread(get_text_embedding, original_title)

            similar_news = []
            for news in all_news:
                if await asyncio.to_thread(compare_embeddings, embed_title, news["embed_title"]) > SIMILARITY_THRESHOLD:
                    similar_news.append(news)
            for news in similar_news:
                all_news.remove(news)

            if len(similar_news) > 0:
                for news in similar_news:
                    await post.edit(name=news["title"])
                    await post.send(news['comment'])
                    await post.send(news['published'])
                    for image in news.get('images', []):
                        await post.send(image)
                    await post.send(news['content']+"\n")
                    await post.send("\n原文：" + news['link'])
        
        for news in all_news:
            available_tags = channel.available_tags
            tag_names = await asyncio.to_thread(determine_tags, available_tags, news['content'])
            forum_tags = [tag for tag in available_tags if tag.name in tag_names]
            thread = await channel.create_thread(name=news["title"], content=news['comment'] + "\n" + news.get('images',[' '])[0], applied_tags=forum_tags, auto_archive_duration=60*24)  # 1 day
            thread = thread.thread
            await thread.send(news['published'])
            for index, image in enumerate(news.get('images', [])):
                if index != 0:
                    await thread.send(image)
            await thread.send(news['content']+"\n")
            await thread.send("原文：" + news['link'])

    print("所有論壇貼文處理完成。")

async def forum_test(bot, id, data):
    channel = bot.get_channel(id)
    if channel is None:
        print(f"無法找到頻道 ID: {id}")
        return
    
    for thread in channel.threads:
        print(thread)  
        await thread.send(data)
