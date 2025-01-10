import discord
from discord.ext import commands, tasks
import os
import asyncio
import random
from services.openai_gpt_processing_service import generate_discord_status
from utils.json_utils import load_json
from config.config import DATA_FOLDER

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()

    @tasks.loop(minutes=5)  # Change status every 5 minutes
    async def change_status(self):
        news_memory_file = os.path.join(DATA_FOLDER, "news_memory.json")
        news_memory = await asyncio.to_thread(load_json, news_memory_file)
        if not isinstance(news_memory, list):
            news_memory = []

        # Get a random news title
        random_news_title = random.choice(news_memory)["title"]
        new_status = generate_discord_status(random_news_title)
        
        # Use Gaming activity type if "正在玩" is in the new_status, otherwise use Custom activity type
        if "正在玩" in new_status:
            activity = discord.Game(name=new_status[4:])
        else:
            activity = discord.CustomActivity(name=new_status)
        
        await self.bot.change_presence(status=discord.Status.online,activity=activity)

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StatusCog(bot))