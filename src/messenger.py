from dataclasses import dataclass
from config import Config
import numpy as np

from api.generic_api import GenericApi
from api.discord_embeds import DiscordEmbeds

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

    def send_status(self, msg: str):
        self._message_api.send_status(msg)        

    def send_message(self, title: str, msg: str, img=""):
        self._message_api.send_message(title, msg, img)

if __name__ == "__main__":
    messenger = Messenger()

    item = "magic_gg_club"
    image = "./info_screenshots/info_pather_got_stuck_20220105_030427.png"
    location = "Shenk"

    # messenger.send_item(item, img, location)
    # messenger.send_death(location, "./info_screenshots/info_pather_got_stuck_20220105_030427.png")
    # messenger.send_chicken(location, "./info_screenshots/info_debug_chicken_20211220_110621.png")
    # messenger.send_stash()
    # messenger.send_gold()
    #messenger.send_item(item, image, location)
    messenger.send_status("test")
    messenger.send_message("Uber Diablo has been FOUND!", f"Dclone IP Found on IP: FUCK", "https://i.psnprofiles.com/games/3bffee/trophies/11Lf29256.png")	
