import keyboard
import os
import threading
from beautifultable import BeautifulTable
import time
import logging
import cv2
import traceback

# from version import __version__
# from utils.graphic_debugger import run_graphic_debugger
# from utils.auto_settings import adjust_settings
# from utils.misc import kill_thread

from config import Config
# from screen import Screen
from logger import Logger
# from game_recovery import GameRecovery
# from game_stats import GameStats
# from health_manager import HealthManager
# from death_manager import DeathManager
# from bot import Bot

from messenger import Messenger

if __name__ == "__main__":



    import keyboard
    import os
    from screen import Screen
    
    from config import Config
    
    from item import ItemCropper

    # keyboard.add_hotkey('f12', lambda: os._exit(1))
    cropper = ItemCropper()
    screen = Screen(cropper._config.general["monitor"])

    # while 1:
    img = screen.grab()
    # res = cropper.crop(img)
    # for cluster in res:
    #     x, y, w, h = cluster.roi
    #     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
    # cv2.imshow("res", img)
    # cv2.waitKey(1)
    # cv2.imwrite("./loot_screenshots/uniq_test.png", img)
    messenger = Messenger()
    msgData = {}
    msgData["type"] = "item"
    msgData["item"] = "other_test"
    msgData["image"] = img
    msgData["location"] = "Shenk"
    # msgData["image"] = "loot_screenshots/uniq_test.png"
    # Logger.debug(f"Main {msgData}")
    messenger._send(msgData)
    
    # msgData["item"] = "magic_test"
    # Logger.debug(f"Main {msgData}")
    # messenger._send(msgData)
    
    # msgData["item"] = "set_test"
    # Logger.debug(f"Main {msgData}")
    # messenger._send(msgData)
    
    msgData["item"] = "rune_test"
    # Logger.debug(f"Main {msgData}")
    messenger._send(msgData)
    
    # msgData["item"] = "uniq_test"
    # Logger.debug(f"Main {msgData}")
    # messenger._send(msgData)
    
    # msgData["item"] = "gray_test"
    # Logger.debug(f"Main {msgData}")
    # messenger._send(msgData)
    
    msgData["type"] = "chicken"
    # Logger.debug(f"Main {msgData}")
    messenger._send(msgData)
    
    msgData["type"] = "death"
    # Logger.debug(f"Main {msgData}")
    messenger._send(msgData)
