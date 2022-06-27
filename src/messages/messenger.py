from dataclasses import dataclass
from config import Config
import numpy as np

from messages.generic_api import GenericApi
from messages.discord_embeds import DiscordEmbeds


class Messenger:
    def __init__(self):
        if Config().general["message_api_type"] == "generic_api":
            self._message_api = GenericApi()
        elif Config().general["message_api_type"] == "discord":
            self._message_api = DiscordEmbeds()
        else:
            self._message_api = None
        self.enabled = Config().general["message_api_type"] and Config().general["custom_message_hook"]


    def send_item(self, item: str, image:  np.ndarray, location: str, ocr_text: str = '', bnip_keep_expression: str = '', item_props = {}):
        self._message_api.send_item(item, image, location, ocr_text, bnip_keep_expression, item_props)

    def send_death(self, location: str, image_path: str = None):
        self._message_api.send_death(location, image_path)

    def send_chicken(self, location: str, image_path: str = None):
        self._message_api.send_chicken(location, image_path)

    def send_stash(self):
        self._message_api.send_stash()

    def send_gold(self):
        self._message_api.send_gold()

    def send_message(self, msg: str):
        self._message_api.send_message(msg)

if __name__ == "__main__":
    messenger = Messenger()

    item = "rune_test"
    image = None
    location = "Shenk"

    # messenger.send_item(item, img, location)
    # messenger.send_death(location, "./log/screenshots/info/info_debug_chicken_20211220_110621.png")
    # messenger.send_chicken(location, "./log/screenshots/info/info_debug_chicken_20211220_110621.png")
    messenger.send_stash()
    messenger.send_gold()
    messenger.send_message("This is a test message")
