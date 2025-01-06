import os
import asyncio
import logging
import json

import discord
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

DATA_FOLDER = "data"
FORUM_CHANNELS_FILE = os.path.join(DATA_FOLDER, "forum_channels.json")

async def main_discord_loop():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("請在 .env 或環境變數中設定 DISCORD_TOKEN")

    intents = discord.Intents.all()

    bot = commands.Bot(
        command_prefix="    ",
        intents=intents,
        heartbeat_timeout=60  # Increase the heartbeat timeout to 60 seconds
    )

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        try:
            synced = await bot.tree.sync()
            await bot.tree.sync(guild=discord.Object(id=1122098259981254688))
            print(f"已同步 {len(synced)} 個指令。")
        except Exception as e:
            print(f"同步指令時發生錯誤: {e}")

    # 建立 data/ 資料夾、forum_channels.json 檔案 (若不存在)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(FORUM_CHANNELS_FILE):
        with open(FORUM_CHANNELS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    # 載入 Cogs
    await bot.load_extension("cogs.forum_config_cog")
    await bot.load_extension("cogs.news_scheduler")

    await bot.start(token)

def main():
    try:
        asyncio.run(main_discord_loop())
    except KeyboardInterrupt:
        logging.info("Bot 已關閉。")

if __name__ == "__main__":
    main()