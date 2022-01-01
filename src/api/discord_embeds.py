from config import Config
import discord
from discord import Webhook, RequestsWebhookAdapter, Color


class DiscordEmbeds:
    def __init__(self):
        self._config = Config()
        
    def send(self, msgData):
            webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter())

            e = discord.Embed(title="Title", description=f"{msgData['item']}", color=Color.dark_gold())
            e.add_field(name="Field 1", value="Value 1")
            e.add_field(name="Field 2", value="Value 2")
            file = discord.File(msgData['image'], filename="image.png")
            e.set_image(url="attachment://image.png")
            webhook.send(embed=e, file=file)
