import requests
import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import tasks, commands

from datetime import datetime

class NotionClient():
    token = os.getenv("NOTION_API_TOKEN")
    databaseId = os.getenv("NOTION_DATABASE_ID")
    headers = {
        "Authorization": "Bearer " + token,
        "Notion-Version": os.getenv("NOTION_API_VERSION")
    }

    lastUpdate = datetime.now()

    def fetch_last_done_tasks(self):
        print(f"Fetching tasks done since : {self.lastUpdate.isoformat()}")

        url = f"https://api.notion.com/v1/databases/{self.databaseId}/query"
        filter = {
            "and": [
                {
                    "property": "Status",
                    "select": {
                        "equals": "Done 🙌"
                    }
                },
                {
                    "property": "Modifié le",
                    "date": {
                        "after": self.lastUpdate.isoformat()
                    }
                }
            ]
        }

        request = requests.post(url=url, headers=self.headers, json={
            "filter": filter
        })

        self.lastUpdate = datetime.now()

        return request.json()["results"]

    def setLastUpdate(self, lastUpdate):
        self.lastUpdate = lastUpdate


class DiscordBot(commands.Bot):
    global notion
    notion = NotionClient()
    channel = None

    async def on_ready(self):
        print("Bot ready")
        self.add_command(self.setLastUpdate)
        self.check_notion.start()
        self.channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))


    @tasks.loop(seconds=2)
    async def check_notion(self):
        for task in notion.fetch_last_done_tasks():
            name = task["properties"]["Name"]["title"][0]["plain_text"]
            await self.channel.send(f"Retrieved task : {name}")


    @commands.command(name="setLastUpdate")
    async def setLastUpdate(channel, lastUpdate):
        notion.setLastUpdate(datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%S"))
        await channel.send("LastUpdate updated")



bot = DiscordBot(
    command_prefix="$"
)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))