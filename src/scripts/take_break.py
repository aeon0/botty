from bot_events import hook
from config import Config
import math
from utils.misc import wait, hms
from logger import Logger
import time 

def take_break(instance):
    if Config().general["max_runtime_before_break_m"] and Config().general["break_length_m"]:
        elapsed_time = time.time() - instance._timer
        Logger.debug(f'Session length = {math.ceil(elapsed_time/60)} minutes, max_runtime_before_break_m {Config().general["max_runtime_before_break_m"]}.')

        if elapsed_time > (Config().general["max_runtime_before_break_m"]*60):
            break_msg = f'Ran for {hms(elapsed_time)}, taking a break for {hms(Config().general["break_length_m"]*60)}.'
            Logger.info(break_msg)
            instance._messenger.send_message(break_msg)
            if not instance._pausing:
                instance.toggle_pause()

            wait(Config().general["break_length_m"]*60)

            break_msg = f'Break over, will now run for {hms(Config().general["max_runtime_before_break_m"]*60)}.'
            Logger.info(break_msg)
            instance._messenger.send_message(break_msg)
            if instance._pausing:
                instance.toggle_pause()

            instance._timer = time.time()


hook.Add("on_end_game", "take a break", take_break)