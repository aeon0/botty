from config import Config
import cv2
import datetime
import discord
from version import __version__
from discord import Webhook, RequestsWebhookAdapter, Color

class DiscordEmbeds:
    def __init__(self):
        self._config = Config()
        
    def send(self, msgData):       
        webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter(), )
        file = None
        psnURL = "https://i.psnprofiles.com/games/3bffee/trophies/"
        
        if msgData["type"] == "item":
            imgName = msgData['item'].replace('_', '-')

            cv2.imwrite(f"./loot_screenshots/{msgData['item']}.png", msgData['image'])  
            file = discord.File(f"./loot_screenshots/{msgData['item']}.png", filename=f"{imgName}.png")
            e = discord.Embed(
                title="Item Stashed!",
                description=f"{msgData['item']}", 
                color=self.get_Item_Color( msgData['item']),
            )
            e.set_thumbnail(url=f"{psnURL}41L6bd712.png")
            e.set_image(url=f"attachment://{imgName}.png")

        elif msgData["type"] == "death":
            file = discord.File(msgData['image_path'], filename="death.png")
            e = discord.Embed(title=f"{self._config.general['name']} has died at {msgData['location']}", color=Color.dark_red())
            e.title=(f"{self._config.general['name']} died")
            e.description=(f"Died at {msgData['location']}")
            e.set_thumbnail(url=f"{psnURL}33L5e3600.png")
            e.set_image(url="attachment://death.png")

        elif msgData["type"] == "chicken": 
            file = discord.File(msgData['image_path'], filename="chicken.png")
            e = discord.Embed(title=f"{self._config.general['name']} has chickened at {msgData['location']}", color=Color.dark_grey())
            e.title=(f"{self._config.general['name']} ran away")
            e.description=(f"chickened at {msgData['location']}")  
            e.set_thumbnail(url=f"{psnURL}39Ldf113b.png")
            e.set_image(url="attachment://chicken.png")

        elif msgData["type"] == "gold": 
            e = discord.Embed(title=f"{self._config.general['name']} is rich!", color=Color.dark_grey())
            e.title=(f"{self._config.general['name']} is Rich!")
            e.description=(f"{self._config.general['name']} can't store any more money!\n turning off gold pickup.")  
            e.set_thumbnail(url=f"{psnURL}6L341955.png")

        elif msgData["type"] == "stash": 
            e = discord.Embed(title=f"{self._config.general['name']} has a full stash!", color=Color.dark_grey())
            e.title=(f"{self._config.general['name']} has a full stash!")
            e.description=(f"{self._config.general['name']} has to quit. \n They cannot store anymore items!")  
            e.set_thumbnail(url=f"{psnURL}35L63a9df.png")

        else: #msgData["type"] == "message":
            e = discord.Embed(title=f"Update:", description=f"```{msgData['message']}```", color=Color.dark_teal())
            if not self._config.general['discord_status_condensed']:
                e.set_thumbnail(url=f"{psnURL}36L4a4994.png")
            
        e.set_footer(text=f'Botty v.{__version__} by Aeon')
        e.timestamp=datetime.datetime.today()
        
        webhook.send(embed=e, file=file, username=self._config.general['name'])

    def get_Item_Color(self, item):
        if "magic_" in item:
            return Color.blue()
        elif "set_" in item:
            return Color.green()
        elif "rune_" in item:
            return Color.dark_gold()
        elif "uniq_" in item or "rare" in item:
            return Color.gold()
        elif "gray_" in item:
            return Color.darker_grey()
        else:
            return Color.blue()