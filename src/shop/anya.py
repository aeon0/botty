import datetime
import logging
import os
import time
import math

import keyboard
import numpy as np

from screen import Screen
from config import Config
from logger import Logger
from npc_manager import NpcManager, Npc
from template_finder import TemplateFinder
from utils.custom_mouse import mouse
from utils.misc import wait, load_template, send_discord
import cv2


class ExtendedTemplateFinder(TemplateFinder):
    def __init__(self, screen):
        super().__init__(screen)
        custom_templates = {
            "CLAW1": [load_template("assets/shop/claws/claw1.png", 1.0), 1.0],
            "CLAW2": [load_template("assets/shop/claws/claw2.png", 1.0), 1.0],
            "CLAW3": [load_template("assets/shop/claws/claw3.png", 1.0), 1.0],
            "TO_TRAPS": [load_template("assets/shop/claws/to_traps.png", 1.0), 1.0],
            "3_TO_TRAPS": [load_template("assets/shop/claws/3_to_traps.png", 1.0), 1.0],
            "2_TO_ASSA": [load_template("assets/shop/claws/2_to_assa.png", 1.0), 1.0],
            "TO_LIGHT": [load_template("assets/shop/claws/to_light.png", 1.0), 1.0],
            "TO_WB": [load_template("assets/shop/claws/wb.png", 1.0), 1.0],
            "TO_DS": [load_template("assets/shop/claws/to_ds.png", 1.0), 1.0],
            "TO_VENOM": [load_template("assets/shop/claws/to_venom.png", 1.0), 1.0],
        }
        self._templates.update(custom_templates)


def exit(run_obj):
    run_time = str(datetime.timedelta(seconds=round(time.time() - run_obj.start_time)))
    Logger.info("Exiting shopping mall...")
    print(
        "STATS \truns \t\ttime \t\tias_gloves_seen \tgloves_bought \tclaws_evaluated \tclaws_bought\n"
        f"\t{run_obj.run_count} \t\t{run_time}"
        f"\t\t{run_obj.ias_gloves_seen} \t\t\t{run_obj.gloves_bought} \t\t{run_obj.claws_evaluated} \t\t\t{run_obj.claws_bought}"
    )
    os._exit(0)


def wait_for_loading_screen(screen: Screen, time_out):
    start = time.time()
    while time.time() - start < time_out:
        img = screen.grab()
        is_loading_black_roi = np.average(img[:700, 0:250]) < 4.0
        if is_loading_black_roi:
            return True
    return False


class AnyaShopper:
    """
    Shop at Anya for 20 ias, +3 java skill gloves and more...

    In order to start the shopping bot:
    1.) Run this this file in Python.
    2.) Be ingame in Harrogath (act 5 town).
    3.) Stand close to Anya and the red portal.
    4.) While being ingame, press resume_key (default F11) to start the shopping, and exit_key (default F12) to stop it.
    """

    def __init__(self, config: Config):
        
        # Configurable part, dont touch anything above
        # Set look_for variables to False if you dont like your personal shopper to look for these
        # Obviously something need to be set to True, or your shopper will be very confused
        # For the trap claw scores use:
        # 7 if you are happy with any + to traps or +2 assassin
        # 9 if you want at least +2 assassin or two useful trap stats
        # 11 if you want at least +3 traps or +2 and a sentry bonus
        # Similar for melee claws but not really worth keeping any less that 11 here since you really want both +2 assassin and a useful other stat, feedback needed 
        
        self.look_for_plus_2_gloves = True
        self.look_for_plus_3_gloves = True
        self.look_for_trap_claws = True
        self.trap_claw_min_score = 11
        self.look_for_melee_claws = True
        self.melee_claw_min_score = 11
        
        # Dont touch anything below here
        self._config = config
        self._screen = Screen(config.general["monitor"])
        self._template_finder = ExtendedTemplateFinder(self._screen)
        self._npc_manager = NpcManager(
            screen=self._screen, template_finder=self._template_finder
        )
        self.run_count = 0
        self.start_time = time.time()
        self.ias_gloves_seen = 0
        self.gloves_bought = 0
        
        # Claws config
        self.roi_claw_stats = [0, 0, config.ui_pos["screen_width"] // 2, config.ui_pos["screen_height"] - 100]
        self.roi_vendor = config.ui_roi["vendor_stash"]
        self.rx, self.ry, _, _ = self.roi_vendor
        self.sb_x, self.sb_y = self._screen.convert_screen_to_monitor((180, 77))
        self.c_x, self.c_y = self._screen.convert_screen_to_monitor((config.ui_pos["center_x"], config.ui_pos["center_y"]))
        self.claws_evaluated = 0
        self.claws_bought = 0

    def run(self):
        Logger.info("Personal Anya Shopper at your service! Hang on, running some errands...")
        self.reset_shop()
        self.shop_loop()

    def shop_loop(self):
    
        asset_folder = "assets/shop/gloves/"
                    
        while True:
        
            self._npc_manager.open_npc_menu(Npc.ANYA)
            self._npc_manager.press_npc_btn(Npc.ANYA, "trade")
            time.sleep(0.1)
            img = self._screen.grab()

            # 20 IAS gloves have a unique color so we can skip all others
            ias_glove = self._template_finder.search(
                ref=load_template(asset_folder + "ias_gloves.png", 1.0),
                inp_img=img,
                threshold=0.96,
                roi=self._config.ui_roi["vendor_stash"],
                normalize_monitor=True,
            )
            if ias_glove.valid:
                self.ias_gloves_seen += 1
                mouse.move(*ias_glove.position)
                time.sleep(0.1)
                img = self._screen.grab()
                
                if self.look_for_plus_3_gloves is True:
                    gg_gloves = self._template_finder.search(
                        ref=load_template(
                            asset_folder + "gg_gloves.png", 1.0 # assets for javazon gloves are mixed up, this one need +3 as in the 1080p version
                        ),
                        inp_img=img,
                        threshold=0.80,
                        normalize_monitor=True,
                    )
                    if gg_gloves.valid:
                        mouse.click(button="right")
                        send_discord(f"Bought awesome IAS/+3 gloves!", self._config.general["custom_discord_hook"])
                        Logger.info("IAS/+3 gloves bought!")
                        self.gloves_bought += 1
                        time.sleep(1)

                else:
                    if self.look_for_plus_2_gloves is True:
                        g_gloves = self._template_finder.search(
                            ref=load_template(
                                asset_folder + "g_gloves.png", 1.0 
                            ),
                            inp_img=img,
                            threshold=0.80,
                            normalize_monitor=True,
                        )
                        if g_gloves.valid:
                            mouse.click(button="right")
                            send_discord(f"Bought some decent IAS/+2 gloves", self._config.general["custom_discord_hook"])
                            Logger.info("IAS/+2 gloves bought!")
                            self.gloves_bought += 1
                            time.sleep(1)

            # Select Weapons section
            if self.look_for_trap_claws is True or self.look_for_melee_claws is True:
                mouse.move(self.sb_x, self.sb_y, randomize=3, delay_factor=[0.6, 0.8])
                wait(0.05, 0.1)
                mouse.press(button="left")
                wait(0.3, 0.4)
                # Search for claws
                claw_pos = []
                img = self._screen.grab().copy()
                claw_keys = ["CLAW1", "CLAW2", "CLAW3"]
                for ck in claw_keys:
                    template_match = self._template_finder.search(ck, img, roi=self.roi_vendor)
                    if template_match.valid:
                        (y, x) = np.where(self._template_finder.last_res >= 0.6)
                        for (x, y) in zip(x, y):
                            new_pos = [x + self.rx + 16, y + self.ry + 50]
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
                    x_m, y_m = self._screen.convert_screen_to_monitor(pos)
                    mouse.move(x_m, y_m, randomize=3, delay_factor=[0.5, 0.6])
                    wait(0.5, 0.6)
                    img_stats = self._screen.grab()
                    trap_score = 0
                    melee_score = 0
                    if self._template_finder.search("3_TO_TRAPS", img_stats, roi=self.roi_claw_stats, threshold=0.94).valid:
                        trap_score += 12
                    elif self._template_finder.search("TO_TRAPS", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 8

                    if self._template_finder.search("2_TO_ASSA", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 10
                        melee_score += 10
                    if self._template_finder.search("TO_VENOM", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        melee_score += 6
                    if self._template_finder.search("TO_LIGHT", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 6
                    if self._template_finder.search("TO_WB", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        melee_score += 2
                    if self._template_finder.search("TO_DS", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 4
                        
                    self.claws_evaluated += 1
                    
                    if trap_score > 11 and self.look_for_trap_claws is True:
                        # pick it up
                        mouse.click(button="right")
                        send_discord(f"Bought some terrific trap Claws (score: {trap_score})", self._config.general["custom_discord_hook"])
                        Logger.info(f"Trap Claws (score: {trap_score}) bought!")
                        self.claws_bought += 1
                        time.sleep(1)
                        
                    if melee_score > 11 and self.look_for_melee_claws is True:
                        # pick it up
                        mouse.click(button="right")
                        send_discord(f"Bought some mad melee Claws (score: {melee_score})", self._config.general["custom_discord_hook"])
                        Logger.info(f"Melee Claws (score: {melee_score}) bought!")
                        self.claws_bought += 1
                        time.sleep(1)    

            # Done with this shopping round
            self.reset_shop()
            self.run_count += 1

    def reset_shop(self):
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(self._screen, 2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])
        time.sleep(3)
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(self._screen, 2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])

    def select_by_template(self, template_type: str) -> bool:
        Logger.debug(f"Select {template_type}")
        template_match = self._template_finder.search_and_wait(template_type, time_out=10)
        if template_match.valid:
            x_m, y_m = self._screen.convert_screen_to_monitor(template_match.position)
            mouse.move(x_m, y_m)
            wait(0.1, 0.2)
            mouse.click(button="left")
            return True
        return False

def main():
    config = Config()
    print("Anya Shopper running, click resume key (Default F11) when close to Anya to start shopping")

    anyashopper = AnyaShopper(config)
    keyboard.add_hotkey(config.general["exit_key"], lambda: exit(run_obj=anyashopper))
    
    while True:
        if keyboard.is_pressed(config.general["resume_key"]):
            try:
                anyashopper.run()
            except Exception as e:
                Logger.logger.exception(e)
                exit(anyashopper)
            break
        if keyboard.is_pressed(config.general["graphic_debugger_key"]):
            screen = Screen(config.general["monitor"])
            tf = ExtendedTemplateFinder(screen)
            search_templates = ["CLAW1", "CLAW2", "CLAW3", "TO_TRAPS", "3_TO_TRAPS", "2_TO_ASSA", "TO_LIGHT", "TO_WB", "TO_DS", "TO_VENOM"]
            scores = {}
            while True:
                img = screen.grab()
                display_img = img.copy()
                for template_name in search_templates:
                    template_match = tf.search(template_name, img)
                    scores[template_name] = template_match.score
                    if template_match.valid:
                        pos = template_match.position
                        cv2.putText(display_img, str(template_name), pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.circle(display_img, pos, 7, (255, 0, 0), thickness=5)
                display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
                print(scores)
                cv2.imshow('test', display_img)
                cv2.waitKey(1)
        time.sleep(0.05)


if __name__ == "__main__":
    main()
