from dataclasses import dataclass
from config import Config
import threading

from api import GenericApi
from api import DiscordEmbeds

from logger import Logger

@dataclass
class MsgData:
    type: str = None
    item: str = None
    location: str = None
    message: str = None

class Messenger:
    def __init__(self):
        self._config = Config()

    def _send(self, msgData: MsgData):
        Logger.debug(f"Messenger {msgData}")
        if self._config.general["message_api_type"] == "generic":
            message_api = GenericApi()
        elif self._config.general["message_api_type"] == "discord":
            message_api = DiscordEmbeds()
        else:
            return
        
        message_api.send(msgData)
        
    def send(self, msgData: MsgData):
        if self._config.general["custom_message_hook"]:
            send_message_thread = threading.Thread(
                target=self._send,
                kwargs={"msgData": msgData}
            )
            send_message_thread.daemon = True
            send_message_thread.start()

if __name__ == "__main__":
    messenger = Messenger()
    messenger.send(msg=f" uniq_test")
