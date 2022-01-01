from config import Config
import discord
from discord import Webhook, RequestsWebhookAdapter, Color


class DiscordEmbeds:
    def __init__(self):
        self._config = Config()
        
    def send(self, msgData):       
        webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter())

        if msgData["type"] == "item":             
            e = discord.Embed(title=f"{self._config.general['name']} found an item", description=f"{msgData['item']}", color=Color.dark_gold())
            # file = discord.File(msgData['image'], filename="image.png")
            # e.set_image(url="attachment://image.png")
        elif msgData["type"] == "death":
            msg = f"{self._config.general['name']}: You have died at {msgData['location']}"
            e = discord.Embed(title=f"{self._config.general['name']} has died", description=f"{msgData['item']}", color=Color.dark_red())
            e.add_field(name="Location", value=msgData['location'])

        elif msgData["type"] == "chicken":
            e = discord.Embed(title=f"{self._config.general['name']} has chickened", description=f"{msgData['item']}", color=Color.dark_grey())
            e.add_field(name="Location", value=msgData['location'])

        elif msgData["type"] == "message":
            e = discord.Embed(title=f"{self._config.general['name']} Update", description=f"```{msgData['message']}```", color=Color.dark_teal())

        webhook.send(embed=e)
        # webhook.send(embed=e, file=file)
