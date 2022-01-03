from config import Config
from logger import Logger
import numpy as np

class IApi:
    def __init__(self):
        self._config = Config()

    def send_item(self, item: str, image:  np.ndarray, location: str):
        msg = f"Found {item} at {location}"
        self._send(msg)
        
    def send_death(self, location: str, image_path: str = None):
        msg = f"You have died at {location}"
        self._send(msg)
        
    def send_chicken(self, location: str, image_path: str = None):
        msg = f"You have chickened at {location}"
        self._send(msg)
        
    def send_stash(self):
        msg = f"All stash tabs and character are full of gold, turn of gold pickup"
        self._send(msg)

    def send_gold(self):
        msg = f"All stash is full, quitting"
        self._send(msg)

    def send_message(self, msg: str):
        self._send(msg)


    def _send(self, msg):
        Logger.info(f"{self._config.general['name']}: {msg}")
