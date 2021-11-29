import keyboard
from utils.custom_mouse import mouse
from char.i_char import IChar
from template_finder import TemplateFinder
from ui_manager import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import time
from pather import Pather, Location


class Hammerdin(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False

    def pre_buff(self):
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def _cast_hammers(self, time_in_s: float):
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(0.05, 0.15)
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.05, 0.15)
        if self._skill_hotkeys["blessed_hammer"]:
            keyboard.send(self._skill_hotkeys["blessed_hammer"])
        wait(0.05, 0.15)
        mouse.press(button="left")
        start = time.time()
        i = 0
        while (time.time() - start) < time_in_s:
            wait(0.04, 0.06)
            i += 1
            if i % 20 == 0:
                mouse.release(button="left")
                wait(0.05, 0.12)
                mouse.press(button="left")
        mouse.release(button="left")
        wait(0.01, 0.05)
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _do_redemption(self):
        if self._skill_hotkeys["redemption"]:
            keyboard.send(self._skill_hotkeys["redemption"])
            wait(1.5, 2.0)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self._config.char["static_path_pindle"]:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._cast_hammers(1)
        # pindle sometimes knocks back, get back in
        self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self, time_out=0.1)
        self._cast_hammers(max(1, self._char_config["atk_len_pindle"] - 1))
        wait(0.1, 0.15)
        self._do_redemption()
        return True

    def kill_eldritch(self) -> bool:
        if self._config.char["static_path_eldritch"]:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes(Location.ELDRITCH_SAVE_DIST, Location.ELDRITCH_END, self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_eldritch"])
        wait(0.05, 0.15)
        self._do_redemption()
        return True

    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        self._pather.traverse_nodes(Location.SHENK_SAVE_DIST, Location.SHENK_END, self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_shenk"])
        wait(0.05, 0.15)
        self._do_redemption()
        return True

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(["VIGOR"])
        can_teleport = self._skill_hotkeys["teleport"] and self._ui_manager.is_right_skill_active()
        if  should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui_manager import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
    char.pre_buff()
    pather.traverse_nodes(Location.ELDRITCH_START, Location.ELDRITCH_SAVE_DIST, char)
    char.kill_eldritch()
