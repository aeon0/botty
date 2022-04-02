from messages import Messenger
from bot_events import hook
from config import Config
import time
from scripts.utils.misc import create_msg
from version import __version__

start_time = time.time()

messenger = Messenger()
hook.Add("on_item_keep", "log_discord_item_keep", lambda item_name, img, location, ocr_text, send_message: send_message and messenger.send_item(item_name, img, location, ocr_text))
hook.Add("on_death", "log_discord_death", lambda location, img: messenger.send_death(location, img))
hook.Add("on_chicken", "log_discord_chicken", lambda location, img: messenger.send_chicken(location, img))

def send_status_update(instance, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats):
    if runs > 0:
        if Config().general["discord_status_count"] and runs % Config().general["discord_status_count"] == 0:
            # every discord_status_count game send a message update about current status
            msg = f"Status Report\n{create_msg(instance, start_time, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats)}\nVersion: {__version__}"
            messenger.send_message(msg)