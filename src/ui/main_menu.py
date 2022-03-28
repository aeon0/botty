import time
import keyboard
from config import Config
from utils.misc import wait
from logger import Logger
from ui import error_screens
from ui_manager import detect_screen_object, is_visible, select_screen_object_match, ScreenObjects
import random
import string


def _play_active(match) -> bool:
    return match.name == "PLAY_BTN"

def start_game() -> bool:
    """
    Starting a game. Will wait and retry on server connection issue.
    :return: Bool if action was successful
    """
    Logger.debug("Wait for Play button")
    start = time.time()
    difficulty=Config().general["difficulty"].lower()
    difficulty_key="r" if difficulty == "normal" else "n" if difficulty == "nightmare" else "h"
    while True:
        if (m := detect_screen_object(ScreenObjects.PlayBtn)).valid:
            if _play_active(m):
                # found active play button
                Logger.debug(f"Found Play Btn, select and press key: {difficulty_key}")
                select_screen_object_match(m)
                keyboard.press(difficulty_key)
                break
            # else found inactive play button, continue loop
        else:
            # did not find either active or inactive play button
            Logger.error("start_game: No play button found, not on main menu screen")
            return False
        wait(1,2)
        if time.time() - start > 90:
            Logger.error("start_game: Active play button never appeared")
            return False
    start = time.time()
    while True:
        #check for loading screen
        if is_visible(ScreenObjects.Loading):
            Logger.debug("Found loading screen / creating game")
            keyboard.release(difficulty_key)
            break
        else:
            wait(1,2)
        # check for server issue
        if is_visible(ScreenObjects.ServerError):
            error_screens.handle_error()
            keyboard.release(difficulty_key)
            return start_game()

        if time.time() - start > 15:
            Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
            keyboard.release(difficulty_key)
            return start_game()
    return True

def goto_lobby () -> bool:
        """
        Go from charselection to lobby
        :return: Bool if action was successful
        """
        while 1:
            Logger.debug("Wait for Lobby button")
            if (found_btn_lobby := detect_screen_object(ScreenObjects.Lobby)).valid:
                Logger.debug(f"Found Lobby Btn")
                select_screen_object_match (found_btn_lobby)
                break
        return True

def create_game_lobby () -> bool:
        Logger.debug("Creating game via Lobby")
        while 1:
            if (found_btn_create := detect_screen_object(ScreenObjects.CreateBtn)).valid:      
                select_screen_object_match (found_btn_create)
                break
        while 1:
            if (found_btn_game_name := detect_screen_object(ScreenObjects.GameName)).valid: 
                select_screen_object_match (found_btn_game_name)
                break
        gn = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        pw = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        keyboard.write (gn)
        wait (0.15, 0.25)
        keyboard.send("Tab")
        wait (0.15, 0.25)
        keyboard.write (pw)
        """
        for char in gn:
            keyboard.send(char)
            wait (0.15, 0.25)
        keyboard.send("Tab")
        for char in pw:
            keyboard.send(char)
            wait (0.15, 0.25)
        """
        while 1:
            if (found_btn_game_name := detect_screen_object(ScreenObjects.CreateBtn2)).valid:
                Logger.debug(f"Found Play Btn2")
                select_screen_object_match (found_btn_game_name)
                break
        return gn, pw

def join_game_lobby (gn, pw) -> bool:
        Logger.debug("Joining game via Lobby")
        while 1:
            if (found_join := detect_screen_object(ScreenObjects.Join)).valid:      
                select_screen_object_match (found_join)
                Logger.debug(f"Found Lobby Btn")
                break
        keyboard.write (gn)
        wait (0.15, 0.25)
        keyboard.send("Tab")
        wait (0.15, 0.25)
        keyboard.write (pw)
        """
        for char in gn:
            keyboard.send(char)
            wait (0.15, 0.25)
        keyboard.send("Tab")
        for char in pw:
            keyboard.send(char)
            wait (0.15, 0.25)
        """
        while 1:
            if (found_btn_join := detect_screen_object(ScreenObjects.BtnJoin)).valid:      
                select_screen_object_match (found_btn_join)
                Logger.debug(f"Found Join Btn")
                break

