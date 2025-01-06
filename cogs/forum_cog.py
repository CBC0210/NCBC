import discord
from discord.ext import commands

# 請填入「討論區 (Forum Channel)」的實際 ID
TARGET_FORUM_CHANNEL_ID = 123456789012345678

class ForumCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 你可以在此紀錄「Bot 自動建立的 Thread」ID，方便後續辨識
        self.my_thread_id = None

    # ========== 1) Slash Command：建立或取得帖子並發言 ==========
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot 啟動完成時的初始化行為，可選擇性使用。"""
        print("[ForumCog] 已啟動，等待指令。")

    # 這裡使用 Slash Command
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """監聽所有訊息，如果是特定的 Thread，Bot 可以回覆。"""
        # 先排除 Bot 自己的訊息，避免無限迴圈
        if message.author.bot:
            return

        # 確認訊息所在的頻道是否為「Thread(執行緒)」型態
        if isinstance(message.channel, discord.Thread):
            # 如果我們只想針對「自己建立的那個帖子」做處理，檢查 ID 是否匹配
            if message.channel.id == self.my_thread_id:
                # 例如，Bot 從使用者輸入中解析關鍵字後再回應
                user_text = message.content
                if "你好" in user_text:
                    await message.channel.send(f"{message.author.mention} 你好呀～我是自動回覆！")
                else:
                    await message.channel.send(f"你剛才說的是：{user_text}")

    @discord.app_commands.command(name="create_post", description="在指定的討論區發表一篇新主題並留言")
    async def create_post(self, interaction: discord.Interaction):
        """Slash Command：在特定論壇頻道建立一篇新貼文 (Thread)，並立即發文。"""

        # 取得「論壇頻道」的物件
        forum_channel = interaction.guild.get_channel(TARGET_FORUM_CHANNEL_ID)
        if not forum_channel:
            await interaction.response.send_message("找不到指定的討論區頻道", ephemeral=True)
            return

        # 確認類型必須是 Forum (ChannelType.forum)
        if forum_channel.type != discord.ChannelType.forum:
            await interaction.response.send_message("指定的頻道並不是討論區類型。", ephemeral=True)
            return

        # 在論壇頻道中建立一篇「主題 (Thread)」
        # py-cord 中可使用 start_thread_in_forum / create_thread 功能。
        # 在 py-cord 2.3.2+，可用 forum_channel.create_thread()
        post_title = "機器人自動建立的主題"
        post_content = "大家好，這是 Bot 建立的帖，歡迎留言。"

        # create_thread: name=主題標題, content=首篇訊息, applied_tags=可指定標籤(若討論區有開)
        #   - 也可先 forum_channel.create_forum_post(title="xxx", content="yyy")
        thread = await forum_channel.create_thread(
            name=post_title,
            content=post_content,
        )

        # 記錄該 Thread ID，方便後續在 on_message 判斷
        self.my_thread_id = thread.id

        # 回覆給使用 Slash 指令的使用者，顯示我們在哪裡開了新帖
        await interaction.response.send_message(f"已在論壇頻道建立主題：[{post_title}] (ID: {thread.id})", ephemeral=True)

        # Bot 也可再針對這篇帖子發送更多訊息
        await thread.send("我是機器人，已成功發文～")

async def setup(bot: commands.Bot):
    """py-cord 2.x 的動態 Cog 加載方式"""
    await bot.add_cog(ForumCog(bot))
