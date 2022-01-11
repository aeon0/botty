from config import Config
import numpy as np
import json
import requests

class GenericApi:
    def __init__(self):
        self._config = Config()

    def send_item(self, item: str, image:  np.ndarray, location: str):
        msg = f"Found {item} at {location}"
        title="no"
        img="no"       
        self._send(title, msg, img)
        
    def send_death(self, location: str, image_path: str = None):
        msg = f"You have died at {location}"
        title="no"
        img="no"       
        self._send(title, msg, img)
        
    def send_chicken(self, location: str, image_path: str = None):
        msg = f"You have chickened at {location}"
        title="no"
        img="no"       
        self._send(title, msg, img)
        
    def send_gold(self):
        msg = f"All stash tabs and character are full of gold, turning off gold pickup"
        title="no"
        img="no"       
        self._send(title, msg, img)

    def send_stash(self):
        msg = f"All stash is full, quitting"
        title="no"
        img="no"       
        self._send(title, msg, img)

    def send_status(self, title: str , msg: str, img: str):
        title="no"
        img="no"           
        self._send(title, msg, img)

    def send_message(self, title: str , msg: str, img: str):
        title="no"
        img="no"           
        self._send(title, msg, img)

    def _send(self, title, msg, img):
        msg = f"{self._config.general['name']}: {msg}"
        tit=title
        img1=img
        if self._config.advanced_options['message_highlight']:
            if " magic_" in msg:
                msg = f"```ini\\n[ {msg} \\n```"
            elif " set_" in msg:
                msg = f"```diff\\n+ {msg} \\n```"
            elif " rune_" in msg:
                msg = f"```css\\n[ {msg} ]\\n```"
            elif " uniq_" in msg or "rare" in msg:
                # TODO: It is more gold than yellow, find a better yellow highlight
                msg = f"```fix\\n- {msg} \\n```"
            elif " gray_" in msg:
                msg = f"```python\\n# {msg} \\n```"
            else:
                msg = f"```\\n{msg} \\n```"
        
        url = self._config.general['custom_message_hook']
        if not url:
            return

        headers = {}
        if self._config.advanced_options['message_headers']:
            headers = json.loads(self._config.advanced_options['message_headers'])

        data = json.loads(self._config.advanced_options['message_body_template'].format(msg=msg), strict=False)

        requests.post(url, headers=headers, json=data)
