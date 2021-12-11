from config import Config
import json
import requests


class MessageSender:
    def __init__(self):
        self._config = Config()

    def send_message(self, msg):
        if self._config.general['message_highlight']:
            if " magic_" in msg:
                msg = f"```ini\\n[ {msg} \\n```"
            elif " set_" in msg:
                msg = f"```diff\\n+ {msg} \\n```"
            elif " rune_" in msg:
                msg = f"```css\\n[ {msg} ]\\n```"
            elif " uniq_" in msg or "rare" in msg:
                # TODO: It is more gold than yellow, find a better yellow highlight
                msg = f"```fix\\n- {msg} \\n```"
            elif " eth_" in msg:
                msg = f"```python\\n# {msg} \\n```"
            else:
                msg = f"```\\n{msg} \\n```"

        self._send_message(msg=msg)

    def _send_message(self, msg):
        url = self._config.general['custom_message_hook']
        if not url:
            return

        headers = {}
        if self._config.general['message_headers']:
            headers = json.loads(self._config.general['message_headers'])

        data = json.loads(self._config.general['message_body_template'].format(msg=msg))

        requests.post(url, headers=headers, json=data)


if __name__ == "__main__":
    message_sender = MessageSender()
    message_sender.send_message(msg=f" uniq_test")
