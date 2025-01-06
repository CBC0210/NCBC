import os
import asyncio
import logging

from discord.ext import commands
# 若使用 py-cord 或 nextcord，可以改為：
# from discord.ext import commands

# 可視需求決定是否使用 dotenv
# (pip install python-dotenv)，用於讀取 .env 檔案
from dotenv import load_dotenv

# 假設在 config/ 資料夾中的 config.py，負責讀取/管理設定
# 也可直接在此檔案進行讀取
# from config.config import load_config

# -----------------------------
# 1) 設定 logger，讓我們能夠看到除錯訊息
# -----------------------------
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# -----------------------------
# 2) 主函式 (async)
# -----------------------------
async def main():
    # 2.1) 讀取 .env
    load_dotenv()
    
    # 2.2) 從環境變數取得 Token、API Key 等機密資料
    # 確保你已在 .env 中設定 DISCORD_TOKEN 與 (選擇性) OPENAI_API_KEY
    discord_token = os.getenv("DISCORD_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not discord_token:
        raise ValueError("請在 .env 或環境變數中設定 DISCORD_TOKEN。")

    # 2.3) 建立 Bot 實例
    # 這裡使用 commands.Bot，如果想要 slash command-only 的話，
    # 可以參考 discord.py 3.0+ (未正式釋出) 或其他 fork 庫的實作方式
    intents = commands.Intents.all()  # 或根據需求調整
    bot = commands.Bot(
        command_prefix="!",  # 指令前綴，可自行調整
        intents=intents
    )

    # 2.4) 載入 Cog（示範用），將在 cogs/ 底下的檔案載入
    # 假設我們有 cogs/general_commands.py, cogs/admin_commands.py
    # cogs/openai_commands.py
    # 建議在這裡或 on_ready 中載入
    try:
        # await bot.load_extension("cogs.general_commands")
        # await bot.load_extension("cogs.admin_commands")
        # await bot.load_extension("cogs.openai_commands")
        logging.info("成功載入所有 Cog。")
    except Exception as e:
        logging.error(f"載入 Cog 時發生錯誤: {e}")

    # 2.5) 啟用 Bot
    # 注意：新版 discord.py (2.0+) 可使用 bot.start(token)，並在 asyncio.run(main()) 時管理 event loop
    await bot.start(discord_token)

# -----------------------------
# 3) 程式進入點
# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 若使用 Ctrl+C 結束程序，可在此處進行額外清理
        logging.info("Bot 已關閉。")
