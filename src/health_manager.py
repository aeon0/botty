from template_finder import TemplateFinder
from ui_manager import UiManager
from belt_manager import BeltManager
import cv2
import time
import keyboard
from utils.misc import kill_thread, cut_roi, color_filter, wait
from logger import Logger
from screen import Screen
import numpy as np
import time
from config import Config
from threading import Thread


class HealthManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, belt_manager: BeltManager):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._belt_manager = belt_manager
        self._do_monitor = False
        self._did_chicken = False
        self._last_rejuv = time.time()
        self._last_health = time.time()
        self._last_mana = time.time()
        self._last_merc_healh = time.time()

    def stop_monitor(self):
        self._do_monitor = False

    def did_chicken(self):
        return self._did_chicken

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
        kill_thread(run_thread)
        if self._config.general["info_screenshots"]:
            cv2.imwrite("./info_screenshots/info_debug_chicken_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(self._config.char["stand_still"])
        wait(0.02, 0.05)
        keyboard.release(self._config.char["show_items"])
        time.sleep(0.01)
        self._ui_manager.save_and_exit(does_chicken=True)
        self._did_chicken = True
        self._do_monitor = False

    def start_monitor(self, run_thread: Thread):
        Logger.debug("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        start = time.time()
        while self._do_monitor:
            time.sleep(0.1)
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 3.0
            if not is_loading_black_roi:
                health_percentage = self.get_health(img)
                mana_percentage = self.get_mana(img)
                # check rejuv
                success_drink_rejuv = False
                if health_percentage < self._config.char["take_rejuv_potion_health"] or \
                   mana_percentage < self._config.char["take_rejuv_potion_mana"]:
                    success_drink_rejuv = self._belt_manager.drink_potion("rejuv")
                # in case no rejuv was used, check for chicken, health pot and mana pot usage
                if not success_drink_rejuv:
                    # check health
                    last_drink = time.time() - self._last_health
                    if health_percentage < self._config.char["take_health_potion"] and last_drink > 3.5:
                        self._belt_manager.drink_potion("health")
                        self._last_health = time.time()
                    # give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
                    elif health_percentage < self._config.char["chicken"] and (time.time() - start) > 6:
                        Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
                        self._do_chicken(img, run_thread)
                        break
                    # check mana
                    last_drink = time.time() - self._last_mana
                    if mana_percentage < self._config.char["take_mana_potion"] and last_drink > 4:
                        self._belt_manager.drink_potion("mana")
                        self._last_mana = time.time()
                # check merc
                merc_alive, _ = self._template_finder.search("MERC", img, roi=self._config.ui_roi["merc_icon"])
                if merc_alive:
                    merc_health_percentage = self.get_merc_health(img)
                    last_drink = time.time() - self._last_merc_healh
                    if merc_health_percentage < self._config.char["merc_chicken"]:
                        Logger.warning(f"Trying to chicken, merc HP {(merc_health_percentage*100):.1f}%!")
                        self._do_chicken(img, run_thread)
                        break
                    if merc_health_percentage < self._config.char["heal_rejuv_merc"] and last_drink > 4.0:
                        self._belt_manager.drink_potion("rejuv", merc=True)
                        self._last_merc_healh = time.time()
                    elif merc_health_percentage < self._config.char["heal_merc"] and last_drink > 7.0:
                        self._belt_manager.drink_potion("health", merc=True)
                        self._last_merc_healh = time.time()
        Logger.debug("Stop health monitoring")


# Testing: Start dying or lossing mana and see if it works
if __name__ == "__main__":
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder)
    belt_manager = BeltManager(screen, template_finder)
    manager = HealthManager(screen, template_finder, ui_manager, belt_manager)
    # manager.start_monitor(None)
    mana = manager.get_mana(screen.grab())
    health = manager.get_health(screen.grab())
    print(health, mana)
