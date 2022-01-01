from config import Config
import discord
from discord import Webhook, RequestsWebhookAdapter, Color

class DiscordEmbeds:
    def __init__(self):
        self._config = Config()
        
    def send(self, msgData):       
        webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter())

        if msgData["type"] == "item":             
            e = discord.Embed(title=f"{self._config.general['name']} found an item", description=f"{msgData['item']} at {msgData['location']}", color=self.get_Item_Color( msgData['item']))
            # file = discord.File(msgData['image'], filename="image.png")
            # e.set_image(url="attachment://image.png")
        elif msgData["type"] == "death":
            msg = f"{self._config.general['name']}: You have died at {msgData['location']}"
            e = discord.Embed(title=f"{self._config.general['name']} has died", color=Color.dark_red())
            e.add_field(name="Location", value=msgData['location'])

        elif msgData["type"] == "chicken":
            e = discord.Embed(title=f"{self._config.general['name']} has chickened", color=Color.dark_grey())
            e.add_field(name="Location", value=msgData['location'])

        elif msgData["type"] == "message":
            e = discord.Embed(title=f"{self._config.general['name']} Update", description=f"```{msgData['message']}```", color=Color.dark_teal())

        webhook.send(embed=e)
        # webhook.send(embed=e, file=file)

    def get_Item_Color(self, item):
        if "magic_" in item:
            return Color.blue()
        elif "set_" in item:
            return Color.green()
        elif "rune_" in item:
            return Color.gold()
        elif "uniq_" in item or "rare" in item:
            return Color.dark_gold()
        elif "gray_" in item:
            return Color.darker_grey()
        else:
            return Color.blue()