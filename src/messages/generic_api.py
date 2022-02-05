from config import Config
from logger import Logger
import numpy as np
import json
import requests

class GenericApi:
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
        
    def send_gold(self):
        msg = f"All stash tabs and character are full of gold, turn of gold pickup"
        self._send(msg)

    def send_stash(self):
        msg = f"All stash is full, quitting"
        self._send(msg)

    def send_message(self, msg: str):
        self._send(msg)

    def _send(self, msg: str):
        msg = f"{self._config.general['name']}: {msg}"
        
        url = self._config.general['custom_message_hook']
        if not url:
            return

        headers = {}
        if self._config.advanced_options['message_headers']:
            headers = json.loads(self._config.advanced_options['message_headers'])

        data = json.loads(self._config.advanced_options['message_body_template'].format(msg=msg), strict=False)

        try:
            requests.post(url, headers=headers, json=data)
        except BaseException as err:
            Logger.error("Error sending generic message: " + err)
