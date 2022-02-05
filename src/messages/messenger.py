from dataclasses import dataclass
from inspect import getmembers
from config import Config
import numpy as np

from messages.generic_api import GenericApi
from messages.discord_embeds import DiscordEmbeds


class Messenger:
    def __init__(self):
        self._config = Config()
        if self._config.general["message_api_type"] == "generic_api":
            self._message_api = GenericApi()
        elif self._config.general["message_api_type"] == "discord":
            self._message_api = DiscordEmbeds()
        else:
            self._message_api = None

    def send_item(self, item: str, image:  np.ndarray, location: str):
        self._message_api.send_item(item, image, location)

    def send_death(self, location: str, image_path: str = None):
        self._message_api.send_death(location, image_path)

    def send_chicken(self, location: str, image_path: str = None):
        self._message_api.send_chicken(location, image_path)

    def send_stash(self):
        self._message_api.send_stash()

    def send_gold(self):
        self._message_api.send_gold()

    def send_status(self, title: str, msg: str, img: str):
        self._message_api.send_status(title, msg, img)

    def send_message(self, title: str, msg: str, img: str):
        self._message_api.send_message(title, msg, img)

if __name__ == "__main__":
    import cv2
    from screen import Screen
    from config import Config
    import keyboard
    import os

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")

    screen = Screen()

    messenger = Messenger()

    item = "rune_test"
    image = None
    location = "Shenk"

    discord_embeds = DiscordEmbeds()
    generic_api = GenericApi()

    img = screen.grab()
    basename = "test"
    file = f"./info_screenshots/{basename}.png"
    cv2.imwrite(f"./info_screenshots/{basename}.png", img)
    cv2.imwrite(f"./loot_screenshots/{basename}.png", img)

    # messenger.send_item(item, img, location)
    for message_api in [discord_embeds, generic_api]:
        message_api.send_death(location, file)
        message_api.send_chicken(location, file)
        message_api.send_stash()
        message_api.send_gold()
        message_api.send_item(item=basename, image = img, location = location)
        message_api.send_status(
            msg = f"hello",
            title = f"{Config.general['name']} - Status Report:",
            img="https://i.psnprofiles.com/games/3bffee/trophies/36L4a4994.png"
        )
        message_api.send_message(
            "Uber Diablo has been FOUND!",
            f"Dclone IP Found on IP: FUCK",
            "https://i.psnprofiles.com/games/3bffee/trophies/11Lf29256.png"
        )
