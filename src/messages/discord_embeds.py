from .generic_api import GenericApi
from config import Config
from logger import Logger
import cv2
import datetime
import traceback
import discord
from version import __version__
import numpy as np
from discord import Webhook, RequestsWebhookAdapter, Color, InvalidArgument

class DiscordEmbeds(GenericApi):
    def __init__(self):
        self._file = None
        self._psnURL = "https://i.psnprofiles.com/games/3bffee/trophies/"
        self._webhook = self._get_webhook(Config().general["custom_message_hook"])
        self._loot_webhook = self._get_webhook(Config().general["custom_loot_message_hook"])

    def _get_webhook(self, hook_url: str):
        hook = None
        if not hook_url:
            hook_url = Config().general['custom_message_hook']
        if hook_url:
            try:
                hook = Webhook.from_url(hook_url, adapter=RequestsWebhookAdapter(), )
            except BaseException as e:
                Logger.warning(f"Your custom_message_hook URL {hook_url} is invalid, Discord updates will not be sent")
                Logger.error(f"Error initializing webhook {hook_url}: {e}")
        return hook

    def send_item(self, item: str, image:  np.ndarray, location: str, ocr_text: str = None):
        imgName = item.replace('_', '-')

        _, w, _ = image.shape
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
        self._send_embed(e, self._loot_webhook, file)

    def send_death(self, location, image_path):
        file = self._add_file(image_path, "death.png")
        e = discord.Embed(title=f"{Config().general['name']} has died at {location}", color=Color.dark_red())
        e.title=(f"{Config().general['name']} died")
        e.description=(f"Died at {location}")
        e.set_thumbnail(url=f"{self._psnURL}33L5e3600.png")
        e.set_image(url="attachment://death.png")
        self._send_embed(e, self._webhook, file)

    def send_chicken(self, location, image_path):
        file = self._add_file(image_path, "chicken.png")
        e = discord.Embed(title=f"{Config().general['name']} has chickened at {location}", color=Color.dark_grey())
        e.title=(f"{Config().general['name']} ran away")
        e.description=(f"chickened at {location}")
        e.set_thumbnail(url=f"{self._psnURL}39Ldf113b.png")
        e.set_image(url="attachment://chicken.png")
        self._send_embed(e, self._webhook, file)

    def send_stash(self):
        e = discord.Embed(title=f"{Config().general['name']} has a full stash!", color=Color.dark_grey())
        e.title=(f"{Config().general['name']} has a full stash!")
        e.description=(f"{Config().general['name']} has to quit. \n They cannot store anymore items!")
        e.set_thumbnail(url=f"{self._psnURL}35L63a9df.png")
        self._send_embed(e, self._webhook)

    def send_gold(self):
        e = discord.Embed(title=f"{Config().general['name']} is rich!", color=Color.dark_grey())
        e.title=(f"{Config().general['name']} is Rich!")
        e.description=(f"{Config().general['name']} can't store any more money!\n turning off gold pickup.")
        e.set_thumbnail(url=f"{self._psnURL}6L341955.png")
        self._send_embed(e, self._webhook)

    def send_message(self, msg: str):
        msg = f"{Config().general['name']}: {msg}"
        e = discord.Embed(title=f"Update:", description=f"```{msg}```", color=Color.dark_teal())
        self._send_embed(e, self._webhook)

    def _send_embed(self, e, webhook, file = None):
        e.set_footer(text=f'Botty v.{__version__} by Aeon')
        e.timestamp=datetime.datetime.now(datetime.timezone.utc)
        try:
            webhook.send(embed=e, file=file, username=Config().general['name'])
        except BaseException as err:
            Logger.error(f"Error sending Discord embed: {err}")

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
