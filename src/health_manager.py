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


class HealthManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._do_monitor = False
        self._did_chicken = False
        self._last_health = time.time()
        self._last_mana = time.time()
        self._last_merc_healh = time.time()

    def stop_monitor(self):
        self._do_monitor = False

    def did_chicken(self):
        return self._did_chicken

    def reset_chicken_flag(self):
        self._did_chicken = False

    def _drink_poition(self, img: np.ndarray, potion_type: str, merc: bool = False):
        for i in range(4):
            roi = [
                self._config.ui_pos["potion1_x"] - (self._config.ui_pos["potion_width"] // 2) + i * self._config.ui_pos["potion_next"],
                self._config.ui_pos["potion1_y"] - (self._config.ui_pos["potion_height"] // 2),
                self._config.ui_pos["potion_width"],
                self._config.ui_pos["potion_height"]
            ]
            potion_img = cut_roi(img, roi)
            if self._ui_manager.potion_type(potion_img) == potion_type:
                key = f"potion{i+1}"
                if merc:
                    Logger.debug(f"Give {potion_type} potion in slot {i+1} to merc")
                    keyboard.send(f"left shift + {self._config.char[key]}")
                else:
                    Logger.debug(f"Drink {potion_type} potion in slot {i+1}")
                    keyboard.send(self._config.char[key])
                break

    def get_health(self, img):
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

    def get_mana(self, img):
        mana_rec = [self._config.ui_pos["mana_left"], self._config.ui_pos["mana_top"], self._config.ui_pos["mana_width"], self._config.ui_pos["mana_height"]]
        mana_img = cut_roi(img, mana_rec)
        mask, _ = color_filter(mana_img, [np.array([117, 120, 20]), np.array([121, 255, 255])])
        mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
        return mana_percentage

    def get_merc_health(self, img):
        health_rec = [self._config.ui_pos["merc_health_left"], self._config.ui_pos["merc_health_top"], self._config.ui_pos["merc_health_width"], self._config.ui_pos["merc_health_height"]]
        merc_health_img = cut_roi(img, health_rec)
        merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
        _, health_tresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
        merc_health_percentage = (float(np.sum(health_tresh)) / health_tresh.size) * (1/255.0)
        return merc_health_percentage

    def start_monitor(self, run_thread):
        Logger.debug("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        while self._do_monitor:
            time.sleep(0.1)
            img = self._screen.grab()
            roi = [700, 650, 460, 250]
            is_loading_black_roi = np.average(img[:, 0:500]) < 1.0
            if not is_loading_black_roi:
                # check health
                health_percentage = self.get_health(img)
                last_drink = time.time() - self._last_health
                if health_percentage < self._config.char["take_health_potion"] and last_drink > 2.5:
                    self._drink_poition(img, "health")
                    self._last_health = time.time()
                elif health_percentage < self._config.char["chicken"]:
                    Logger.warning("Trying to chicken!")
                    cv2.imwrite("info_debug_chicken.png", img)
                    self._ui_manager.save_and_exit()
                    self._did_chicken = True
                    kill_thread(run_thread)
                    self._do_monitor = False
                    break
                # check mana
                mana_percentage = self.get_mana(img)
                last_drink = time.time() - self._last_mana
                if mana_percentage < self._config.char["take_mana_potion"] and last_drink > 3.0:
                    self._drink_poition(img, "mana")
                    self._last_mana = time.time()
                # check merc
                roi = [0, 0, 150, 150]
                merc_alive, _ = self._template_finder.search("MERC", img, roi=roi)
                if merc_alive:
                    merc_health_percentage = self.get_merc_health(img)
                    last_drink = time.time() - self._last_merc_healh
                    if merc_health_percentage < self._config.char["heal_merc"] and last_drink > 5.0:
                        self._drink_poition(img, "health", merc=True)
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
