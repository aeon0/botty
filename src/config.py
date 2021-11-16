import configparser
import numpy as np
import os


class Config:
    def _select_val(self, section: str, key: str = None):
        if section in self._custom and key in self._custom[section]:
            return self._custom[section][key]
        elif section in self._config:
            return self._config[section][key]
        else:
            return self._game_config[section][key]

    def __init__(self, print_warnings: bool = False):
        # print_warnings, what a hack... here it is, not making the effort
        # passing a single config instance through bites me in the ass
        self._print_warnings = print_warnings
        self._config = configparser.ConfigParser()
        self._config.read('params.ini')
        self._game_config = configparser.ConfigParser()
        self._game_config.read('game.ini')
        self._custom = configparser.ConfigParser()
        if os.environ.get('RUN_ENV') != "test" and os.path.exists('custom.ini'):
            self._custom.read('custom.ini')

        self.general = {
            "monitor": int(self._select_val("general", "monitor")),
            "res": self._select_val("general", "res"),
            "offset_top": int(self._select_val("general", "offset_top")),
            "min_game_length_s": float(self._select_val("general", "min_game_length_s")),
            "exit_key": self._select_val("general", "exit_key"),
            "resume_key": self._select_val("general", "resume_key"),
            "auto_settings_key": self._select_val("general", "auto_settings_key"),
            "color_checker_key": self._select_val("general", "color_checker_key"),
            "logg_lvl": self._select_val("general", "logg_lvl"),
            "randomize_runs": bool(int(self._select_val("general", "randomize_runs"))),
            "difficulty": self._select_val("general", "difficulty"),
            "send_drops_to_discord": bool(int(self._select_val("general", "send_drops_to_discord"))),
            "custom_discord_hook": self._select_val("general", "custom_discord_hook"),
            "info_screenshots": bool(int(self._select_val("general", "info_screenshots"))),
            "loot_screenshots": bool(int(self._select_val("general", "loot_screenshots"))),
        }

        self.routes = {}
        for key in self._config["routes"]:
            self.routes[key] = bool(int(self._select_val("routes", key)))

        self.char = {
            "type": self._select_val("char", "type"),
            "show_items": self._select_val("char", "show_items"),
            "inventory_screen": self._select_val("char", "inventory_screen"),
            "stand_still": self._select_val("char", "stand_still"),
            "num_loot_columns": int(self._select_val("char", "num_loot_columns")),
            "take_health_potion": float(self._select_val("char", "take_health_potion")),
            "take_mana_potion": float(self._select_val("char", "take_mana_potion")),
            "heal_merc": float(self._select_val("char", "heal_merc")),
            "chicken": float(self._select_val("char", "chicken")),
            "merc_chicken": float(self._select_val("char", "merc_chicken")),
            "tp": self._select_val("char", "tp"),
            "show_belt": self._select_val("char", "show_belt"),
            "potion1": self._select_val("char", "potion1"),
            "potion2": self._select_val("char", "potion2"),
            "potion3": self._select_val("char", "potion3"),
            "potion4": self._select_val("char", "potion4"),
            "es_available": bool(int(self._select_val("char", "es_available"))),
            "ts_available": bool(int(self._select_val("char", "ts_available"))),
            "cta_available": bool(int(self._select_val("char", "cta_available"))),
            "weapon_switch": self._select_val("char", "weapon_switch"),
            "battle_orders": self._select_val("char", "battle_orders"),
            "battle_command": self._select_val("char", "battle_command"),
            "casting_frames": int(self._select_val("char", "casting_frames")),
            "slow_walk": bool(int(self._select_val("char", "slow_walk"))),
            "atk_len_pindle": int(self._select_val("char", "atk_len_pindle")),
            "atk_len_eldritch": int(self._select_val("char", "atk_len_eldritch")),
            "atk_len_shenk": int(self._select_val("char", "atk_len_shenk")),
            "static_path_pindle": bool(int(self._select_val("char", "static_path_pindle"))),
            "static_path_eldritch": bool(int(self._select_val("char", "static_path_eldritch"))),
        }

        self.sorceress = dict(self._config["sorceress"])
        if "sorceress" in self._custom:
            self.sorceress.update(dict(self._custom["sorceress"]))

        self.hammerdin = self._config["hammerdin"]
        if "hammerdin" in self._custom:
            self.hammerdin.update(self._custom["hammerdin"])

        self.items = {}
        for key in self._config["items"]:
            self.items[key] = int(self._select_val("items", key))
            item_folder = "items" if self.general["res"] == "1920_1080" else "items_1280_720"
            if self.items[key] and not os.path.exists(f"./assets/{item_folder}/{key}.png") and self._print_warnings:
                print(f"Warning: You activated {key} in pickit, but there is no asset for {self.general['res']}")

        self.colors = {}
        for key in self._game_config["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)

        self.scale = 1.0 if self.general["res"] == "1920_1080" else 0.666667

        self.ui_pos = {}
        for key in self._game_config["ui_pos_1920_1080"]:
            self.ui_pos[key] = int(round(float(self._select_val("ui_pos_1920_1080", key)) * self.scale))

        self.ui_roi = {}
        for key in self._game_config["ui_roi_1920_1080"]:
            self.ui_roi[key] = np.array([int(round(float(x) * self.scale)) for x in self._select_val("ui_roi_1920_1080", key).split(",")])

        self.path = {}
        for key in self._game_config["path"]:
            self.path[key] = np.reshape(np.array([int(round(float(x) * self.scale)) for x in self._select_val("path", key).split(",")]), (-1, 2))



if __name__ == "__main__":
    config = Config()

    # for k in config.ui_pos:
    #     x = config.ui_pos[k]
    #     print(f"{k}={x}")

    from pathlib import Path
    import cv2

    for k in config.items:
        if not os.path.exists(f"./assets/items/{k}.png"):
            print(f"Template not found: {k}")
            # base_name = k.split("_")[2:]
            # attrib = k.split("_")[0]
            # base_name = '_'.join(base_name)
            # if attrib == "uniq":
            #     # print(f"{base_name}")
            #     for path in Path("./assets/items").glob(f"*_{base_name}.png"):
            #         print(k)
            #         img = cv2.imread(str(path))
            #         cv2.imwrite(f"./assets/items/{k}.png", img)
            # else:
            #     print(f"{attrib}_{base_name}=1")
    
    for filename in os.listdir(f'assets/items'):
        filename = filename.lower()
        if filename.endswith('.png'):
            item_name = filename[:-4]
            blacklist_item = item_name.startswith("bl__")
            if item_name not in config.items:
                print(f"Config not found for: " + filename)
