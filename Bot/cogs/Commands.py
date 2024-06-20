import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, Embed, Interaction

import asyncio
import aiofiles
import random

from .Crawler import get_restaurants, URL_encoding

# 用於儲存每個用戶的餐廳數據
user_restaurant_data = {}

class RestaurantCommands(commands.Cog):
    """
    這個類別包含了與餐廳相關的命令和處理邏輯。
    """

    def __init__(self, bot):
        """
        初始化 RestaurantCommands 類別。

        Args:
            bot (commands.Bot): 機器人實例。
        """
        self.bot = bot

    async def send_error_message(self, interaction: Interaction, title: str, description: str):
        """
        發送錯誤訊息。

        Args:
            interaction (Interaction): Discord 互動對象。
            title (str): 錯誤標題。
            description (str): 錯誤描述。
        """
        error_message = Embed(
            title=title,
            description=description,
            colour=nextcord.Color.red()
        )
        await interaction.followup.send(embed=error_message)
        
    async def send_searching_message(self, interaction: Interaction, landmark: str):
        """
        發送搜尋中的訊息。

        Args:
            interaction (Interaction): Discord 互動對象。
            landmark (str): 地標名稱。
        """
        searching_message = Embed(
            title="搜尋中",
            description=f"正在探索`{landmark}`附近的餐廳...",
            colour=nextcord.Color.yellow()
        )
        await interaction.response.send_message(embed=searching_message)
    
    async def write_restaurant_data_to_file(self, restaurant_data):
        """
        將餐廳數據寫入臨時文件。

        Args:
            restaurant_data (list): 餐廳數據列表。

        Returns:
            str: 臨時文件的路徑。
        """
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as f:
            for name, link in restaurant_data:
                await f.write(f'{name} - {link}\n')
            return f.name

    async def send_search_completed_message(self, interaction: Interaction, landmark: str, file_path: str):
        """
        發送搜尋完成的訊息和附件。

        Args:
            interaction (Interaction): Discord 互動對象。
            landmark (str): 地標名稱。
            file_path (str): 餐廳數據文件的路徑。
        """
        searching_completed_message = Embed(
            title=f"{landmark} - 探索完成",
            description="▼ 勇者の技能 ▼",
            colour=nextcord.Color.green()
        ).add_field(
            name="隨機推薦餐廳",
            value="</ewrandom:1252306339430928466>",
            inline=False
        ).add_field(
            name="「新增or重新探索」地標的鄰近餐廳",
            value="</eatwhat:1252306335610044427>",
            inline=False
        )
        
        user_mention = interaction.user.mention
        
        await interaction.followup.send(
            embed=searching_completed_message,
            content=f"## Notify: {user_mention} - 敬愛的踩雷勇者\n**▼ 攻 略 `{landmark}` ， 贏 得 榮 耀 ▼**",
            file=nextcord.File(file_path, filename='restaurant_list.txt')
        )

    @nextcord.slash_command(name="eatwhat", description="搜尋附近的餐廳")
    async def eatwhat(self, interaction: Interaction, landmark: str = SlashOption(description="你想搜尋的地標")):
        """
        slash命令: 搜尋附近的餐廳。

        Args:
            interaction (Interaction): Discord 互動對象。
            landmark (str): 地標名稱。
        """
        user_id = interaction.user.id
        request_id = landmark

        user_restaurant_data.setdefault(user_id, {})[request_id] = []

        await self.send_searching_message(interaction, landmark)

        try:
            encoding_landmark = URL_encoding(f"{landmark}附近餐廳")
            restaurant_data = await asyncio.to_thread(get_restaurants, encoding_landmark)
            user_restaurant_data[user_id][request_id] = restaurant_data

            file_path = await self.write_restaurant_data_to_file(restaurant_data)
            await self.send_search_completed_message(interaction, landmark, file_path)

        except Exception as e:
            await self.send_error_message(interaction, "錯誤！", f"搜尋餐廳時發生錯誤：{e}")

    @nextcord.slash_command(name="ewrandom", description="隨機推薦餐廳")
    async def ewrandom(self, interaction: Interaction, request_id: str = SlashOption(description="你想搜尋的地標")):
        """
        slash命令: 隨機推薦餐廳。

        Args:
            interaction (Interaction): Discord 互動對象。
            request_id (str): 地標名稱。
        """
        user_id = interaction.user.id

        if user_id not in user_restaurant_data or request_id not in user_restaurant_data[user_id] or not user_restaurant_data[user_id][request_id]:
            not_have_restaurant_data_message = Embed(
                title="目前沒有任何餐廳資料！",
                description="請先進行探索：",
                colour=nextcord.Color.red()
            ).add_field(
                name="搜尋該地標的鄰近餐廳",
                value="</eatwhat:1252306335610044427>",
                inline=False
            )
            await interaction.response.send_message(embed=not_have_restaurant_data_message)
            return

        random_restaurant = random.choice(user_restaurant_data[user_id][request_id])
        name, link = random_restaurant
        await interaction.response.send_message(f"## [{request_id}] {name}\n{link}")

    @ewrandom.on_autocomplete("request_id")
    async def ewrandom_autocomplete(self, interaction: Interaction, query: str):
        """
        自動填入的選單: 提供可用的地標名稱。

        Args:
            interaction (Interaction): Discord 互動對象。
            query (str): 使用者輸入的查詢字符串。
        """
        user_id = interaction.user.id
        if user_id in user_restaurant_data:
            request_ids = [request_id for request_id in user_restaurant_data[user_id].keys() if query.lower() in request_id.lower()]
            await interaction.response.send_autocomplete(request_ids[:25])

    @nextcord.slash_command(name="ewclear", description="清除指定地標的餐廳資料")
    async def ewclear(self, interaction: Interaction, request_id: str = SlashOption(description="你想清除的地標")):
        """
        slash命令: 清除指定地標的餐廳資料。

        Args:
            interaction (Interaction): Discord 互動對象。
            request_id (str): 地標名稱。
        """
        user_id = interaction.user.id

        if user_id not in user_restaurant_data or request_id not in user_restaurant_data[user_id]:
            not_have_restaurant_data_message = Embed(
                title="目前沒有任何餐廳資料！",
                description="請先進行探索：",
                colour=nextcord.Color.red()
            ).add_field(
                name="搜尋該地標的鄰近餐廳",
                value="</eatwhat:1252306335610044427>",
                inline=False
            )
            await interaction.response.send_message(embed=not_have_restaurant_data_message)
            return

        del user_restaurant_data[user_id][request_id]

        cleared_message = Embed(
            title="已清除餐廳數據",
            description=f"清除 `{request_id}` 成功。",
            colour=nextcord.Color.red()
        )
        await interaction.response.send_message(embed=cleared_message)

    @ewclear.on_autocomplete("request_id")
    async def ewclear_autocomplete(self, interaction: Interaction, query: str):
        """
        自動填入的選單: 提供可用的地標名稱。

        Args:
            interaction (Interaction): Discord 互動對象。
            query (str): 使用者輸入的查詢字符串。
        """
        user_id = interaction.user.id
        if user_id in user_restaurant_data:
            request_ids = [request_id for request_id in user_restaurant_data[user_id].keys() if query.lower() in request_id.lower()]
            await interaction.response.send_autocomplete(request_ids[:25])

def setup(bot):
    """
    設置 cog。

    Args:
        bot (commands.Bot): 機器人實例。
    """
    bot.add_cog(RestaurantCommands(bot))
