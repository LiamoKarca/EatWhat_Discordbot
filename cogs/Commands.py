import asyncio
import random

import nextcord
from nextcord import SlashOption, Embed, Interaction, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import Button, View

from .Crawler import get_restaurants, url_encoding

# Global variable to store user-specific restaurant data
USER_RESTAURANT_DATA = {}


def get_error_embed_message(error_embed_message: Exception) -> Embed:
    """
    Create an error message embed.

    Args:
        error_embed_message (Exception): The error message.

    Returns:
        nextcord.Embed: The error message embed.
    """
    return Embed(
        title="錯誤！",
        description=str(error_embed_message),
        colour=nextcord.Color.red()
    )


def get_searching_message(landmark: str) -> Embed:
    """
    Create a message indicating that the restaurant search is in progress.

    Args:
        landmark (str): The name of the landmark.

    Returns:
        nextcord.Embed: The searching message embed.
    """
    embed_message = Embed(
        title="搜尋中",
        description=f"正在探索 `{landmark}` 附近的餐廳...",
        colour=nextcord.Color.yellow()
    )
    return embed_message


async def get_restaurants_data(restaurant_data) -> tuple:
    """
    Format the restaurant data into chunks of 10 restaurants each.

    Args:
        restaurant_data (list): The list of restaurant data.

    Returns:
        tuple: A tuple containing the formatted restaurant data chunks and the number of chunks.
    """
    chunk_size = 10
    chunks = [restaurant_data[i:i + chunk_size] for i in range(0, len(restaurant_data), chunk_size)]
    return chunks, len(chunks)


def check_user_data(user_id: int, request_id: str) -> bool:
    """
    Check if the user_id and request_id exist in the user_restaurant_data.

    Args:
        user_id (int): The ID of the user.
        request_id (str): The ID of the request.

    Returns:
        bool: True if both user_id and request_id exist in the user_restaurant_data, False otherwise.
    """
    return user_id in USER_RESTAURANT_DATA and request_id in USER_RESTAURANT_DATA[user_id]


def check_restaurant_data(user_id: int, request_id: str) -> bool:
    """
    Check if the user_id and request_id exist in the user_restaurant_data and if the corresponding data is not empty.

    Args:
        user_id (int): The ID of the user.
        request_id (str): The ID of the request.

    Returns: bool: True if both user_id and request_id exist in the user_restaurant_data and the data is not empty,
    False otherwise.
    """
    return user_id in USER_RESTAURANT_DATA and request_id in USER_RESTAURANT_DATA[user_id] and \
        USER_RESTAURANT_DATA[user_id][request_id]


class RestaurantCommands(commands.Cog):
    """
    This class contains commands and logic related to restaurants.
    """

    def __init__(self, bot):
        self.bot = bot
        self.landmark = None
        self.page = 0
        self.current_data = None
        self.max_chunks = 0
        self.view = None
        self.message = None

    def get_completed_message(self, interaction: Interaction, landmark: str, restaurants_list: list):
        """
        Generate a completed message with restaurant recommendations.

        Args:
            interaction (Interaction): The Discord interaction object.
            landmark (str): The name of the landmark.
            restaurants_list (list): The list of restaurant data.

        Returns:
            dict: A dictionary containing the embed message.
        """
        formatted_restaurants = [f"[{restaurant['name']}]({restaurant['link']})" for restaurant in restaurants_list]

        title = "踩雷地點"
        if self.max_chunks > 1:
            title = f"踩雷地點 - 頁數 {self.page + 1}/{self.max_chunks}"

        restaurants_embed = Embed(
            title=title,
            description="\n".join(formatted_restaurants),
            colour=nextcord.Color.gold()
        )

        user_mention = interaction.user.mention
        searching_completed_message = [
            Embed(
                title="勇者，這是你的踩雷菜單",
                description=f"致敬勇者：{user_mention}",
                colour=nextcord.Color.blue()
            ),
            restaurants_embed,
            Embed(
                title=f"{landmark} - 探索完成",
                description="▼ 你可以嘗試以下指令 ▼",
                colour=nextcord.Color.green()
            ).add_field(
                name="隨機推薦餐廳",
                value="</ewrandom:1253382872853905468>",
                inline=False
            ).add_field(
                name="「新增 or 重新探索」地標的鄰近餐廳",
                value="</eatwhat:1253768332675514432>",
                inline=False
            )
        ]

        message = {
            "embed": searching_completed_message,
        }

        return message

    @nextcord.slash_command(name="eatwhat", description="Search nearby restaurants", guild_ids=[479164051230818306])
    async def eatwhat(self, interaction: Interaction, landmark: str = SlashOption(description="Landmark to search")):
        """
        Slash command to search for nearby restaurants.

        Args:
            interaction (Interaction): The Discord interaction object.
            landmark (str): The name of the landmark to search.
        """
        user_id = interaction.user.id

        USER_RESTAURANT_DATA.setdefault(user_id, {})[landmark] = []
        embed_message = get_searching_message(landmark=landmark)

        self.message = await interaction.send(embed=embed_message)

        try:
            encoding_landmark = url_encoding(f"{landmark} 附近餐廳")
            restaurant_data = await asyncio.to_thread(get_restaurants, encoding_landmark)
            USER_RESTAURANT_DATA[user_id][landmark] = restaurant_data

            self.current_data, self.max_chunks = await get_restaurants_data(USER_RESTAURANT_DATA[user_id][landmark])
            self.page = 0
            self.landmark = landmark
            await self.update_embed(interaction)

        except Exception as e:
            embed_message = get_error_embed_message(error_embed_message=e)
            await self.message.edit(embed=embed_message)

    async def update_embed(self, interaction: Interaction):
        """
        Update the embed message with restaurant data.

        Args:
            interaction (Interaction): The Discord interaction object.
        """
        chunk = self.current_data[self.page]
        message_data = self.get_completed_message(interaction, self.landmark, chunk)

        prev_button = Button(label="上一頁", custom_id="prev")
        next_button = Button(label="下一頁", custom_id="next")

        if self.page == 0:
            prev_button.disabled = True
            prev_button.style = ButtonStyle.red
        else:
            prev_button.disabled = False
            prev_button.style = ButtonStyle.green

        if self.page == self.max_chunks - 1:
            next_button.disabled = True
            next_button.style = ButtonStyle.red
        else:
            next_button.disabled = False
            next_button.style = ButtonStyle.green

        self.view = View()
        self.view.add_item(prev_button)
        self.view.add_item(next_button)

        await interaction.edit_original_message(embeds=message_data["embed"], view=self.view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        """
        Listener for interactions with the bot. If the interaction is a button click (previous or next),
        it triggers the corresponding function to update the embed message with restaurant data.

        Args:
            interaction (Interaction): The Discord interaction object.
        """
        if 'custom_id' not in interaction.data:
            return

        if interaction.data['custom_id'] == "prev":
            await self.prev_button(interaction)
        elif interaction.data['custom_id'] == "next":
            await self.next_button(interaction)

    async def prev_button(self, interaction: nextcord.Interaction):
        if self.page > 0:
            self.page -= 1
            await self.update_embed(interaction)

    async def next_button(self, interaction: nextcord.Interaction):
        if self.page < self.max_chunks - 1:
            self.page += 1
            await self.update_embed(interaction)

    @nextcord.slash_command(name="ewrandom", description="隨機推薦餐廳", guild_ids=[479164051230818306])
    async def ewrandom(self, interaction: Interaction, request_id: str = SlashOption(description="你想搜尋的地標")):
        """
        Slash command to randomly recommend a restaurant.

        Args:
            interaction (Interaction): The Discord interaction object.
            request_id (str): The name of the landmark to search.

        If no restaurant data is available for the given landmark, a message is sent to the user to first explore the
        landmark. If restaurant data is available, a random restaurant is recommended.
        """
        user_id = interaction.user.id

        if not check_restaurant_data(user_id, request_id):
            embed_message = Embed(
                title="目前沒有任何餐廳資料！",
                description="請先進行探索：",
                colour=nextcord.Color.red()
            ).add_field(
                name="搜尋該地標的鄰近餐廳",
                value="</eatwhat:1252306335610044427>",
                inline=False
            )
            await interaction.response.send_message(embed=embed_message)
            return

        random_restaurant = random.choice(USER_RESTAURANT_DATA[user_id][request_id])
        embed_message = Embed(
            title=request_id,
            description=f"[{random_restaurant['name']}]({random_restaurant['link']})",
            colour=nextcord.Color.gold()
        )

        await interaction.response.send_message(embeds=[embed_message])

    @ewrandom.on_autocomplete("request_id")
    async def ewrandom_autocomplete(self, interaction: Interaction, query: str):
        """
        Autocomplete menu: Provides available landmark names.

        Args:
            interaction (Interaction): The Discord interaction object.
            query (str): The query string input by the user.

        If the user has restaurant data, it provides an autocomplete list of landmarks that match the user's query.
        """
        user_id = interaction.user.id
        if user_id in USER_RESTAURANT_DATA:
            request_ids = [request_id for request_id in USER_RESTAURANT_DATA[user_id].keys() if
                           query.lower() in request_id.lower()]
            await interaction.response.send_autocomplete(request_ids[:25])

    @nextcord.slash_command(name="ewclear", description="清除指定地標的餐廳資料", guild_ids=[479164051230818306])
    async def ewclear(self, interaction: Interaction, request_id: str = SlashOption(description="你想清除的地標")):
        """
        Slash command to clear restaurant data for a specific landmark.

        Args:
            interaction (Interaction): The Discord interaction object.
            request_id (str): The name of the landmark to clear.

        If no restaurant data is available for the given landmark, a message is sent to the user to first explore the
        landmark. If restaurant data is available, the data for the specific landmark is deleted.
        """
        user_id = interaction.user.id

        if not check_user_data(user_id, request_id):
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

        del USER_RESTAURANT_DATA[user_id][request_id]

        cleared_message = Embed(
            title="已清除餐廳數據",
            description=f"清除 `{request_id}` 成功。",
            colour=nextcord.Color.red()
        )
        await interaction.response.send_message(embed=cleared_message)

    @ewclear.on_autocomplete("request_id")
    async def ewclear_autocomplete(self, interaction: Interaction, query: str):
        """
        Autocomplete menu: Provides available landmark names.

        Args:
            interaction (Interaction): The Discord interaction object.
            query (str): The query string input by the user.

        If the user has restaurant data, it provides an autocomplete list of landmarks that match the user's query.
        """
        user_id = interaction.user.id
        if user_id in USER_RESTAURANT_DATA:
            request_ids = [request_id for request_id in USER_RESTAURANT_DATA[user_id].keys() if
                           query.lower() in request_id.lower()]
            await interaction.response.send_autocomplete(request_ids[:25])


def setup(bot):
    bot.add_cog(RestaurantCommands(bot))
