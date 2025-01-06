import os
import discord
from discord.ext import commands
from discord import app_commands

# 從 utils/json_utils.py 匯入
from utils.json_utils import load_json, save_json

DATA_FOLDER = "data"
FORUM_CHANNELS_FILE = os.path.join(DATA_FOLDER, "forum_channels.json")

class ForumConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.forum_channels_data = {}

    async def cog_load(self):
        """在 Cog 被載入時呼叫，讀取 JSON 檔案。"""
        # 使用我們的 load_json 函式
        self.forum_channels_data = load_json(FORUM_CHANNELS_FILE, default_data={})

    async def save_forum_channels(self):
        """將 self.forum_channels_data 寫回 JSON。"""
        save_json(FORUM_CHANNELS_FILE, self.forum_channels_data)

    @app_commands.command(name="add_forum_channel", description="將新的論壇頻道ID加入機器人記憶")
    @app_commands.describe(channel="要加入的論壇頻道")
    @app_commands.guild_only()
    async def add_forum_channel(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        """只有管理員可使用，將論壇頻道ID存到JSON中。"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("你沒有管理員權限，無法使用此指令。", ephemeral=True)
            return

        guild_id_str = str(interaction.guild_id)

        # 初始化該guild的清單
        if guild_id_str not in self.forum_channels_data:
            self.forum_channels_data[guild_id_str] = []

        # 檢查是否已存在
        if channel.id in self.forum_channels_data[guild_id_str]:
            await interaction.response.send_message(f"論壇頻道 {channel.mention} 已在列表中。", ephemeral=True)
            return

        # 新增 ID
        self.forum_channels_data[guild_id_str].append(channel.id)
        await self.save_forum_channels()  # 寫檔

        await interaction.response.send_message(
            f"已將論壇頻道 {channel.mention} (ID: {channel.id}) 加入紀錄。",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ForumConfigCog(bot))
