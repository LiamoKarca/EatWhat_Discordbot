import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import logging

def load_environment_variables():
    """
    載入環境變數。
    """
    load_dotenv()

def setup_logging():
    """
    設置日誌記錄。
    """
    logging.basicConfig(level=logging.INFO, format='[DISCORD_BOT_INFO] %(message)s')

def get_bot() -> commands.Bot:
    """
    設置機器人並返回。

    Returns:
        commands.Bot: 配置好的機器人實例。
    """
    intents = nextcord.Intents.default()
    intents.members = True
    intents.message_content = True  # 啟用 message_content intent

    bot = commands.Bot(command_prefix='/', intents=intents)
    return bot

def load_cogs(bot: commands.Bot, cogs: list):
    """
    載入所有的cogs。

    Args:
        bot (commands.Bot): 機器人實例。
        cogs (list): cogs的名稱列表。
    """
    for cog in cogs:
        bot.load_extension(cog)

async def on_ready_handler(bot: commands.Bot):
    """
    當機器人成功登錄時的事件處理函數。

    Args:
        bot (commands.Bot): 機器人實例。
    """
    logging.info(f'Logged in as {bot.user}')
    await bot.change_presence(
        status=nextcord.Status.online,
        activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="commands")
    )

def main():
    """
    主函數，用於運行機器人。
    """
    load_environment_variables()
    setup_logging()

    bot = get_bot()

    @bot.event
    async def on_ready():
        await on_ready_handler(bot)

    cogs = ['Bot.cogs.Commands']
    load_cogs(bot, cogs)

    bot.run(os.getenv("BOT_API"))

if __name__ == "__main__":
    main()
