from template_finder import TemplateFinder
from ui_manager import UiManager
import cv2
import time
import keyboard
from utils.misc import kill_thread, cut_roi, color_filter
from logger import Logger
from screen import Screen
import numpy as np
import time
from config import Config
from threading import Thread
from belt_manager import BeltManager


class HealthManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, belt_manager: BeltManager):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._belt_manager = belt_manager
        self._do_monitor = False
        self._did_chicken = False
        self._last_health = time.time()
        self._last_rejuv = time.time()
        self._last_mana = time.time()
        self._last_merc_healh = time.time()
        self._last_merc_rejuv = time.time()

    def stop_monitor(self):
        self._do_monitor = False

    def did_chicken(self):
        return self._did_chicken

    def _drink_potion(self, potion_type: str, percentage: float, merc: bool = False):
        key=f""
        for i in range(4):
            if self._belt_manager.potions_remaining[i] > 0 and self._config.char['belt_slots'][i] == potion_type:
                key = f"potion{i+1}"
                if merc:
                    Logger.debug(f"Give {potion_type} in slot {i+1} to merc, val={(percentage*100):.1f}%")
                    keyboard.send(f"left shift + {self._config.char[key]}")
                else:
                    Logger.debug(f"Drink {potion_type} in slot {i+1}, val={(percentage*100):.1f}%")
                    keyboard.send(self._config.char[key])
                self._belt_manager.potions_remaining[i] = self._belt_manager.potions_remaining[i] - 1
                break
        if not key:
            #Logger.debug(f"Out of {potion_type}")

    def get_health(self, img: np.ndarray) -> float:
        health_rec = [self._config.ui_pos["health_left"], self._config.ui_pos["health_top"], self._config.ui_pos["health_width"], self._config.ui_pos["health_height"]]
        health_img = cut_roi(img, health_rec)
        # red mask
        mask1, _ = color_filter(health_img, [np.array([0, 110, 20]), np.array([2, 255, 255])])
        mask2, _ = color_filter(health_img, [np.array([178, 110, 20]), np.array([180, 255, 255])])
        mask = cv2.bitwise_or(mask1, mask2)
        health_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
        # green (in case of poison)
        mask, _ = color_filter(health_img, [np.array([47, 90, 20]), np.array([54, 255, 255])])
        health_percentage_green = (float(np.sum(mask)) / mask.size) * (1/255.0)
        return max(health_percentage, health_percentage_green)

    def get_mana(self, img: np.ndarray) -> float:
        mana_rec = [self._config.ui_pos["mana_left"], self._config.ui_pos["mana_top"], self._config.ui_pos["mana_width"], self._config.ui_pos["mana_height"]]
        mana_img = cut_roi(img, mana_rec)
        mask, _ = color_filter(mana_img, [np.array([117, 120, 20]), np.array([121, 255, 255])])
        mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
        return mana_percentage

    def get_merc_health(self, img: np.ndarray) -> float:
        health_rec = [self._config.ui_pos["merc_health_left"], self._config.ui_pos["merc_health_top"], self._config.ui_pos["merc_health_width"], self._config.ui_pos["merc_health_height"]]
        merc_health_img = cut_roi(img, health_rec)
        merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
        _, health_tresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
        merc_health_percentage = (float(np.sum(health_tresh)) / health_tresh.size) * (1/255.0)
        return merc_health_percentage

    def _do_chicken(self, img, run_thread):
        cv2.imwrite("info_debug_chicken.png", img)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(self._config.char["stand_still"])
        keyboard.release(self._config.char["show_items"])
        time.sleep(0.01)
        self._ui_manager.save_and_exit(does_chicken=True)
        self._did_chicken = True
        kill_thread(run_thread)
        self._do_monitor = False

    def start_monitor(self, run_thread: Thread):
        Logger.debug("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        start = time.time()
        while self._do_monitor:
            time.sleep(0.1)
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.0
            if not is_loading_black_roi:
                # check health
                health_percentage = self.get_health(img)
                last_rejuv_drink = time.time() - self._last_rejuv
                last_drink = time.time() - self._last_health

                # give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
                if health_percentage < self._config.char["chicken"] and (time.time() - start) > 6:
                    Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
                    self._do_chicken(img, run_thread)
                    break
                elif health_percentage < self._config.char["take_rejuvenation_potion_health"] and last_rejuv_drink > 3:
                    self._drink_potion("rejuvenation_potion",health_percentage)
                    self._last_rejuv = time.time()
                elif health_percentage < self._config.char["take_healing_potion"] and last_drink > 3.5 and last_rejuv_drink > 1.5:
                    self._drink_potion("healing_potion",health_percentage)
                    self._last_health = time.time()
                # check mana
                mana_percentage = self.get_mana(img)
                last_drink = time.time() - self._last_mana
                last_rejuv_drink = time.time() - self._last_rejuv
                if mana_percentage < self._config.char["take_rejuvenation_potion_mana"] and last_rejuv_drink > 4:
                    self._drink_potion("rejuvenation_potion",mana_percentage)
                    self._last_mana = time.time()
                elif mana_percentage < self._config.char["take_mana_potion"] and last_drink > 4 and last_rejuv_drink > 2:
                    self._drink_potion("mana_potion",mana_percentage)
                    self._last_mana = time.time()
                # check merc
                merc_alive, _ = self._template_finder.search("MERC", img, roi=self._config.ui_roi["merc_icon"])
                if merc_alive:
                    merc_health_percentage = self.get_merc_health(img)
                    last_drink = time.time() - self._last_merc_healh
                    last_merc_rejuv_drink = time.time() - self._last_merc_rejuv
                    if merc_health_percentage < self._config.char["merc_chicken"]:
                        Logger.warning(f"Trying to chicken, merc HP {(merc_health_percentage*100):.1f}%!")
                        self._do_chicken(img, run_thread)
                        break
                    elif merc_health_percentage < self._config.char["heal_rejuvenation_merc"] and last_merc_rejuv_drink > 5.0:
                        self._drink_potion("rejuvenation_potion", merc_health_percentage, merc=True)
                        self._last_merc_rejuv = time.time()
                    elif merc_health_percentage < self._config.char["heal_merc"] and last_drink > 7.0 and last_rejuv_drink > 3:
                        self._drink_potion("healing_potion", merc_health_percentage, merc=True)
                        self._last_merc_healh = time.time()
        Logger.debug("Stop health monitoring")


# Testing: Start dying or lossing mana and see if it works
if __name__ == "__main__":
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder)
    manager = HealthManager(screen, template_finder, ui_manager)
    # manager.start_monitor(None)
    mana = manager.get_mana(screen.grab())
    health = manager.get_health(screen.grab())
    print(health, mana)
