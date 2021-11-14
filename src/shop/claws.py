from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from template_finder import TemplateFinder, load_template
from ui_manager import UiManager
from utils.custom_mouse import mouse
from utils.misc import wait, send_discord
import keyboard
import numpy as np
import cv2
import os
from char.sorceress import Sorceress
from pather import Pather
import math
import time


class ExtendedTemplateFinder(TemplateFinder):
    def __init__(self, screen):
        super().__init__(screen)
        custom_templates = {
            "ANYA_FRONT": [load_template("assets/npc_1280_720/anya/anya_front.png", 1.0), 1.0],
            "ANYA_BACK": [load_template("assets/npc_1280_720/anya/anya_back.png", 1.0), 1.0],
            "ANYA_SIDE": [load_template("assets/npc_1280_720/anya/anya_side.png", 1.0), 1.0],
            "ANYA_NAME_TAG_GOLD": [load_template("assets/npc_1280_720/anya/anya_gold.png", 1.0), 1.0],
            "ANYA_NAME_TAG_WHITE": [load_template("assets/npc_1280_720/anya/anya_white.png", 1.0), 1.0],
            "ANYA_TRADE_BTN": [load_template("assets/npc_1280_720/anya/trade_btn.png", 1.0), 1.0],
            "CLAW1": [load_template("assets/shop_1280_720/claws/claw1.png", 1.0), 1.0],
            "CLAW2": [load_template("assets/shop_1280_720/claws/claw2.png", 1.0), 1.0],
            "CLAW3": [load_template("assets/shop_1280_720/claws/claw3.png", 1.0), 1.0],
            "TO_TRAPS": [load_template("assets/shop_1280_720/claws/to_traps.png", 1.0), 1.0],
            "3_TO_TRAPS": [load_template("assets/shop_1280_720/claws/3_to_traps.png", 1.0), 1.0],
            "2_TO_ASSA": [load_template("assets/shop_1280_720/claws/2_to_assa.png", 1.0), 1.0],
            "TO_LIGHT": [load_template("assets/shop_1280_720/claws/to_light.png", 1.0), 1.0],
            "TO_WB": [load_template("assets/shop_1280_720/claws/wb.png", 1.0), 1.0],
            "TO_DS": [load_template("assets/shop_1280_720/claws/to_ds.png", 1.0), 1.0],
            "SHOP_PORTAL": [load_template("assets/shop_1280_720/claws/a5_red.png", 1.0), 1.0],
            "TO_VENOM": [load_template("assets/shop_1280_720/claws/to_venom.png", 1.0), 1.0],
        }
        self._templates.update(custom_templates)


def wait_for_loading_screen(screen: Screen, time_out):
    start = time.time()
    while time.time() - start < time_out:
        img = screen.grab()
        is_loading_black_roi = np.average(img[:700, 0:250]) < 4.0
        if is_loading_black_roi:
            return True
    return False


if __name__ == "__main__":
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")

    config = Config()
    screen = Screen(config.general["monitor"])
    tf = ExtendedTemplateFinder(screen)
    npc = NpcManager(screen, tf)
    ui = UiManager(screen, tf)
    pather = Pather(screen, tf)
    char = Sorceress(config.sorceress, config.char, screen, tf, ui, pather)

    roi_claw_stats = [0, 0, config.ui_pos["screen_width"] // 2, config.ui_pos["screen_height"] - 100]
    roi_vendor = config.ui_roi["vendor_stash"]
    rx, ry, _, _ = roi_vendor
    sb_x, sb_y = screen.convert_screen_to_monitor((180, 77))
    c_x, c_y = screen.convert_screen_to_monitor((config.ui_pos["center_x"], config.ui_pos["center_y"]))

    while 1:
        # Open shop
        if not npc.open_npc_menu(Npc.ANYA):
            send_discord("Shutting down shopping", config.general["custom_discord_hook"])
            img = screen.grab()
            cv2.imwrite("stuck.png", img)
            # close_down_d2()
            break
        mouse.move(c_x + 50, c_y - 100, randomize=30, delay_factor=[0.5, 0.7])
        npc.press_npc_btn(Npc.ANYA, "trade")
        wait(1.0, 1.2)
        # Select claw section
        mouse.move(sb_x, sb_y, randomize=3, delay_factor=[0.6, 0.8])
        wait(0.05, 0.1)
        mouse.press(button="left")
        wait(0.3, 0.4)
        # Search for claws
        claw_pos = []
        img = screen.grab().copy()
        claw_keys = ["CLAW1", "CLAW2", "CLAW3"]
        for ck in claw_keys:
            found, _ = tf.search(ck, img, roi=roi_vendor)
            if found:
                (y, x) = np.where(tf.last_res >= 0.6)
                for (x, y) in zip(x, y):
                    new_pos = [x + rx + 16, y + ry + 50]
                    # check if pos already exists in claw_pos
                    exists_already = False
                    for pos in claw_pos:
                        dist = math.dist(new_pos, pos)
                        if dist < 10:
                            exists_already = True
                    if not exists_already:
                        claw_pos.append(new_pos)
        # check out each claw
        for pos in claw_pos:
            # cv2.circle(img, pos, 3, (0, 255, 0), 2)
            x_m, y_m = screen.convert_screen_to_monitor(pos)
            mouse.move(x_m, y_m, randomize=3, delay_factor=[0.5, 0.6])
            wait(0.5, 0.6)
            img_stats = screen.grab()
            score = 0
            if tf.search("3_TO_TRAPS", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 9
            elif tf.search("TO_TRAPS", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 7

            if tf.search("2_TO_ASSA", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 7
            if tf.search("TO_VENOM", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 7
            if tf.search("TO_LIGHT", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 7
            if tf.search("TO_WB", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 2
            if tf.search("TO_DS", img_stats, roi=roi_claw_stats, threshold=0.9)[0]:
                score += 5

            if score > 10:
                # pick it up
                mouse.click(button="right")
                send_discord(f"Bought_CLAWS (score: {score})", config.general["custom_discord_hook"])
        # cv2.imshow("x", img)
        # cv2.waitKey(0)
        wait(0.4, 0.6)
        keyboard.send("esc")
        # Refresh by going to portal
        char.select_by_template("SHOP_PORTAL")
        wait(2.3, 2.7)
        while 1:
            success = char.select_by_template("SHOP_PORTAL")
            success &= wait_for_loading_screen(screen, 2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])
