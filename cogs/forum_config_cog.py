import os
import discord
from discord.ext import commands
from discord import app_commands

# 從 utils/json_utils.py 匯入
from utils.json_utils import load_json, save_json
from config.config import FORUM_CHANNELS_FILE, NCBC_DISCRIPTION, NCBC_FORUM_TAGS

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
        """初始化論壇頻道。"""
        existing_tags = {tag.name: tag for tag in channel.available_tags}
        new_tags = {tag.name: tag for tag in NCBC_FORUM_TAGS}

        # Remove tags that are not in the new_tags
        for tag_name in list(existing_tags.keys()):
            if tag_name not in new_tags:
                await channel.delete_tag(existing_tags[tag_name])

        # Add new tags that are not in the existing_tags
        for tag_name, tag in new_tags.items():
            if tag_name not in existing_tags:
                await channel.create_tag(name=tag.name)

        # Update the available_tags with the new tags
        # updated_tags = [tag for tag in channel.available_tags if tag.name in new_tags]
        await channel.edit(
            name="NCBC新聞臺",
            topic=NCBC_DISCRIPTION,
            default_layout=discord.ForumLayoutType.gallery_view
        )
    @app_commands.command(name="remove_forum_channel", description="從機器人的使用列表中移除論壇頻道")
    @app_commands.describe(channel="要移除的論壇頻道")
    @app_commands.guild_only()
    async def remove_forum_channel(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        """只有管理員可使用，將論壇頻道ID從JSON中移除。"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("你沒有管理員權限，無法使用此指令。", ephemeral=True)
            return

        guild_id_str = str(interaction.guild_id)
        
        # 檢查頻道是否存在於該guild中
        if guild_id_str not in self.forum_channels_data or channel.id not in self.forum_channels_data[guild_id_str]:
            await interaction.response.send_message(f"論壇頻道 {channel.mention} 不在列表中。", ephemeral=True)
            return

        # 移除 ID
        self.forum_channels_data[guild_id_str].remove(channel.id)
        await self.save_forum_channels()  # 寫檔

        await interaction.response.send_message(
            f"已將論壇頻道 {channel.mention} (ID: {channel.id}) 從紀錄中移除。",
            ephemeral=True
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
