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
            return self._ui_config[section][key]

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read('params.ini')
        self._ui_config = configparser.ConfigParser()
        self._ui_config.read('ui.ini')
        self._custom = configparser.ConfigParser()
        if os.path.exists('custom.ini'):
             self._custom.read('custom.ini')

        self.general = {
            "monitor": int(self._select_val("general", "monitor")),
            "min_game_length_s": float(self._select_val("general", "min_game_length_s")),
            "exit_key": self._select_val("general", "exit_key"),
            "resume_key": self._select_val("general", "resume_key"),
            "auto_settings_key": self._select_val("general", "auto_settings_key"),
            "color_checker_key": self._select_val("general", "color_checker_key"),
            "logg_lvl": self._select_val("general", "logg_lvl"),
            "randomize_runs": bool(int(self._select_val("general", "randomize_runs"))),
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
            "tp": self._select_val("char", "tp"),
            "show_belt": self._select_val("char", "show_belt"),
            "potion1": self._select_val("char", "potion1"),
            "potion2": self._select_val("char", "potion2"),
            "potion3": self._select_val("char", "potion3"),
            "potion4": self._select_val("char", "potion4"),
            "cta_available": bool(int(self._select_val("char", "cta_available"))),
            "weapon_switch": self._select_val("char", "weapon_switch"),
            "battle_orders": self._select_val("char", "battle_orders"),
            "battle_command": self._select_val("char", "battle_command"),
            "casting_frames": int(self._select_val("char", "casting_frames")),
            "slow_walk": bool(int(self._select_val("char", "slow_walk"))),
            "atk_len_pindle": int(self._select_val("char", "atk_len_pindle")),
            "atk_len_eldritch": int(self._select_val("char", "atk_len_eldritch")),
            "atk_len_shenk": int(self._select_val("char", "atk_len_shenk")),
            "static_path_pindle": int(self._select_val("char", "static_path_pindle")),
            "static_path_eldritch": int(self._select_val("char", "static_path_eldritch")),
        }

        self.sorceress = dict(self._config["sorceress"])
        if "sorceress" in self._custom:
            self.sorceress.update(dict(self._custom["sorceress"]))

        self.hammerdin = self._config["hammerdin"]
        if "hammerdin" in self._custom:
            self.hammerdin.update(self._custom["hammerdin"])

        self.items = {}
        for key in self._config["items"]:
            self.items[key] = bool(int(self._select_val("items", key)))

        self.colors = {}
        for key in self._ui_config["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)

        self.ui_pos = {}
        for key in self._ui_config["ui_pos_1920_1080"]:
            self.ui_pos[key] = int(self._select_val("ui_pos_1920_1080", key))

        self.ui_roi = {}
        for key in self._ui_config["ui_roi_1920_1080"]:
            self.ui_roi[key] = np.array([int(x) for x in self._select_val("ui_roi_1920_1080", key).split(",")])


if __name__ == "__main__":
    config = Config()
