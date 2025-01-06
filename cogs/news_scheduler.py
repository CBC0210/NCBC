# cogs/news_scheduler.py
import discord
from discord.ext import commands, tasks
import asyncio

from services.forum_post_service import forum_test
# 從 config.py 取得排程秒數
from config.config import NEWS_FETCH_INTERVAL

# 從 services 裡匯入新聞處理函式
from services.news_processer import process_yahoo_news

class NewsSchedulerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 在 Cog 初始化時啟動背景任務
        self.fetch_news_bg_task.start()

    def cog_unload(self):
        # 若此 Cog 被卸載，記得要停止背景任務
        self.fetch_news_bg_task.cancel()

    @tasks.loop(seconds=NEWS_FETCH_INTERVAL)
    async def fetch_news_bg_task(self):
        """
        每隔 NEWS_FETCH_INTERVAL 秒，自動抓取一次 Yahoo 新聞並處理。
        """
        try:
            print("[NewsSchedulerCog] 正在抓取新聞...")
            # 使用 asyncio.to_thread 執行同步函式，避免阻塞事件循環
            #await forum_test(self.bot, 1325665805408403456, "test")
            await process_yahoo_news(self.bot)
            print("[NewsSchedulerCog] 抓取並處理成功。")
        except Exception as e:
            print(f"[NewsSchedulerCog] 抓取新聞發生錯誤: {e}")

    @fetch_news_bg_task.before_loop
    async def before_fetch_news(self):
        """
        在背景任務正式開始前，先等待機器人準備就緒。
        """
        print("[NewsSchedulerCog] 等待 Bot 就緒中...")
        await self.bot.wait_until_ready()
        print("[NewsSchedulerCog] Bot 已就緒，開始排程抓新聞。")

    # 新增的 Slash Command
    @commands.hybrid_command(
        name="fetchnews",
        description="手動抓取最新的新聞。"
    )
    async def fetch_news_command(self, ctx: commands.Context):
        """
        當使用者輸入 /fetchnews 時，手動觸發新聞抓取與處理。
        """
        await ctx.defer()  # 延遲回應，避免超時

        try:
            print("[NewsSchedulerCog] 手動抓取新聞中...")
            # 使用 asyncio.to_thread 執行同步函式
            await process_yahoo_news(self.bot)
            print("[NewsSchedulerCog] 手動抓取並處理成功。")
            await ctx.send("✅ 已成功手動抓取最新的 Yahoo奇摩新聞並處理。")
        except Exception as e:
            print(f"[NewsSchedulerCog] 手動抓取新聞發生錯誤: {e}")
            await ctx.send(f"❌ 手動抓取新聞時發生錯誤：{e}")

    # 處理命令錯誤
    @fetch_news_command.error
    async def fetch_news_command_error(self, ctx: commands.Context, error: Exception):
        """
        處理 /fetchnews 命令的錯誤。
        """
        print(f"[NewsSchedulerCog] /fetchnews 命令錯誤: {error}")
        await ctx.send(f"❌ 發生錯誤：{error}")

async def setup(bot: commands.Bot):
    # 動態載入 Cog 用的 async setup
    await bot.add_cog(NewsSchedulerCog(bot))
