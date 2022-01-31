from .generic_api import GenericApi
from config import Config
import cv2
import datetime
import traceback
import discord
from version import __version__
import numpy as np
from discord import Webhook, RequestsWebhookAdapter, Color

class DiscordEmbeds(GenericApi):
    def __init__(self):
        self._config = Config()
        self._webhook = Webhook.from_url(self._config.general['custom_message_hook'], adapter=RequestsWebhookAdapter(), )
        self._file = None
        self._psnURL = "https://i.psnprofiles.com/games/3bffee/trophies/"

    def send_item(self, item: str, image:  np.ndarray, location: str, ocr_text: str):
        imgName = item.replace('_', '-')

        # _, w, _ = image.shape
        # image = image[:, (w//2):,:]
        cv2.imwrite(f"./loot_screenshots/{item}.png", image)
        file = self._add_file(f"./loot_screenshots/{item}.png", f"{imgName}.png")
        e = discord.Embed(
            title="Item Stashed!",
            description=f"{item} at {location}",
            color=self._get_Item_Color( item),
        )
        e.set_thumbnail(url=f"{self._psnURL}41L6bd712.png")
        e.set_image(url=f"attachment://{imgName}.png")
        e.add_field(name="OCR Text", value=f"{ocr_text}", inline=False)

        self._send_embed(e, file)

    def send_death(self, location, image_path):
        file = self._add_file(image_path, "death.png")
        e = discord.Embed(title=f"{self._config.general['name']} has died at {location}", color=Color.dark_red())
        e.title=(f"{self._config.general['name']} died")
        e.description=(f"Died at {location}")
        e.set_thumbnail(url=f"{self._psnURL}33L5e3600.png")
        e.set_image(url="attachment://death.png")
        self._send_embed(e, file)

    def send_chicken(self, location, image_path):
        file = self._add_file(image_path, "chicken.png")
        e = discord.Embed(title=f"{self._config.general['name']} has chickened at {location}", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} ran away")
        e.description=(f"chickened at {location}")
        e.set_thumbnail(url=f"{self._psnURL}39Ldf113b.png")
        e.set_image(url="attachment://chicken.png")
        self._send_embed(e, file)

    def send_stash(self):
        e = discord.Embed(title=f"{self._config.general['name']} has a full stash!", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} has a full stash!")
        e.description=(f"{self._config.general['name']} has to quit. \n They cannot store anymore items!")
        e.set_thumbnail(url=f"{self._psnURL}35L63a9df.png")
        self._send_embed(e)

    def send_gold(self):
        e = discord.Embed(title=f"{self._config.general['name']} is rich!", color=Color.dark_grey())
        e.title=(f"{self._config.general['name']} is Rich!")
        e.description=(f"{self._config.general['name']} can't store any more money!\n turning off gold pickup.")
        e.set_thumbnail(url=f"{self._psnURL}6L341955.png")
        self._send_embed(e)

    def send_message(self, msg: str):
        msg = f"{self._config.general['name']}: {msg}"
        e = discord.Embed(title=f"Update:", description=f"```{msg}```", color=Color.dark_teal())
        if not self._config.general['discord_status_condensed']:
            e.set_thumbnail(url=f"{self._psnURL}36L4a4994.png")
        self._send_embed(e)

    def _send_embed(self, e, file = None):
        e.set_footer(text=f'Botty v.{__version__} by Aeon')
        e.timestamp=datetime.datetime.now(datetime.timezone.utc)

        self._webhook.send(embed=e, file=file, username=self._config.general['name'])

    def _get_Item_Color(self, item):
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

    def _add_file(self, image_path, image_name):
        try: 
            return discord.File(image_path, filename=image_name)
        except:
            traceback.print_exc()
            return discord.File("./assets/error/image_not_found.png", filename=image_name)
