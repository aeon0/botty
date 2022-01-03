from dataclasses import dataclass
from config import Config
import json
import requests

class GenericApi:
    def __init__(self):
        self._config = Config()

    def send(self, msgData):
        if msgData["type"] == "item":
             msg = f"{self._config.general['name']}: Found {msgData['item']} at {msgData['location']}"
        elif msgData["type"] == "death":
            msg = f"{self._config.general['name']}: You have died at {msgData['location']}"
        elif msgData["type"] == "chicken":
            msg = f"{self._config.general['name']}: You have chickened at {msgData['location']}"
        elif msgData["type"] == "gold":
            msg = f"{self._config.general['name']}: All stash tabs and character are full of gold, turn of gold pickup"
        elif msgData["type"] == "stash":
            msg = f"{self._config.general['name']}: All stash is full, quitting"
        elif msgData["type"] == "message":
            msg = msgData['message']

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

        self._send(msg=msg)

    def get_location_msg(self,location):
        if location is not None:
            return f" at {location}"
        else: 
            return ""

    def _send(self, msg):
        url = self._config.general['custom_message_hook']
        if not url:
            return

        headers = {}
        if self._config.advanced_options['message_headers']:
            headers = json.loads(self._config.advanced_options['message_headers'])

        data = json.loads(self._config.advanced_options['message_body_template'].format(msg=msg), strict=False)

        requests.post(url, headers=headers, json=data)


if __name__ == "__main__":
    generalApi = GenericApi()
    generalApi.send(msg=f" uniq_test")
