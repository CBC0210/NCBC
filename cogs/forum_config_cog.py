import os
import discord
from discord.ext import commands
from discord import app_commands

# 從 utils/json_utils.py 匯入
from utils.json_utils import load_json, save_json
from config.config import FORUM_CHANNELS_FILE

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

    async def initialize_channel(self, channel: discord.ForumChannel):
        await channel.edit(
            name="NCBC新聞臺",
            topic=("歡迎來到NCBC論壇！\n\n"
                   "這裡專注於收集和分享經過篩選的新聞內容。"
                   "CBC 不喜歡那些吸引點擊但內容空洞的農場標題和文章，因此在這裡，你會看到經過轉換和整理的高質量新聞。"
                   "\n我們致力於提供清晰、直接的新聞報導，不包含多餘的內容。"
                   "在這裡，你可以和其他成員一起討論時事，分享觀點，增進理解。"
                   "\n我也會和大家分享我的看法。"
                   "\n別再説「宅宅不懂時事」了。NCBC希望每位成員都能輕鬆掌握最新的社會動態，提升你的時事敏感度。"),
            available_tags=[
                discord.ForumTag(name="公告"),
                discord.ForumTag(name="運動新聞"),
                discord.ForumTag(name="電玩遊戲"),
                discord.ForumTag(name="新聞報導"),
                discord.ForumTag(name="時事討論"),
                discord.ForumTag(name="科技動態"),
                discord.ForumTag(name="政治討論"),
                discord.ForumTag(name="經濟分析"),
                discord.ForumTag(name="健康資訊"),
                discord.ForumTag(name="環保話題"),
                discord.ForumTag(name="文化藝術"),
                discord.ForumTag(name="問題與解答"),
                discord.ForumTag(name="資源分享"),
                discord.ForumTag(name="深入分析"),
                discord.ForumTag(name="評論與見解"),
                discord.ForumTag(name="未來趨勢"),
                discord.ForumTag(name="迷因與趣味"),
                discord.ForumTag(name="隨機話題"),
                discord.ForumTag(name="投票"),
                discord.ForumTag(name="娛樂新聞"),
            ]
        )

    @app_commands.command(name="add_forum_channel", description="將論壇頻道給機器人使用，已經被使用的頻道會被初始化")
    @app_commands.describe(channel="要加入的論壇頻道")
    @app_commands.guild_only()
    async def add_forum_channel(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        """只有管理員可使用，將論壇頻道ID存到JSON中。"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("你沒有管理員權限，無法使用此指令。", ephemeral=True)
            return

        guild_id_str = str(interaction.guild_id)
        # 檢查頻道是否存在於該guild中
        channel_in_guild = interaction.guild.get_channel(channel.id)
        if channel_in_guild is None:
            await interaction.response.send_message("指定的頻道不存在於此伺服器。", ephemeral=True)
            return
        
        # 初始化該guild的清單
        if guild_id_str not in self.forum_channels_data:
            self.forum_channels_data[guild_id_str] = []

        # 檢查是否已存在
        if channel.id in self.forum_channels_data[guild_id_str]:
            await interaction.response.send_message(f"論壇頻道 {channel.mention} 已在列表中。", ephemeral=True)
            await self.initialize_channel(channel)  # 初始化頻道
            return

        # 新增 ID
        self.forum_channels_data[guild_id_str].append(channel.id)
        await self.initialize_channel(channel)  # 初始化頻道
        await self.save_forum_channels()  # 寫檔

        await interaction.response.send_message(
            f"已將論壇頻道 {channel.mention} (ID: {channel.id}) 加入紀錄。",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ForumConfigCog(bot))
