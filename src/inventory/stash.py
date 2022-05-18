import template_finder
from screen import grab, convert_screen_to_monitor
from config import Config
import os
from utils.misc import wait
from utils.custom_mouse import mouse
from logger import Logger
from messages import Messenger

curr_stash = {
    "items": 3 if Config().char["fill_shared_stash_first"] else 0,
    "gold": 0
}

def get_curr_stash() -> dict:
    global curr_stash
    return curr_stash

def set_curr_stash(items: int = None, gold: int = None):
    global curr_stash
    if items is not None: curr_stash["items"] = items
    if gold is not None: curr_stash["gold"] = gold

def stash_full():
    Logger.error("All stash is full, quitting")
    if Config().general["custom_message_hook"]:
        Messenger().send_stash()
    os.system("taskkill /f /im  D2R.exe")
    wait(1.0, 1.5)
    os._exit(0)