import configparser
import numpy as np


class Config:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('params.ini')
        ui_config = configparser.ConfigParser()
        ui_config.read('ui.ini')

        self.general = {
            "monitor": int(config["general"]["monitor"]),
            "min_game_length_s": float(config["general"]["min_game_length_s"]),
            "exit_key": config["general"]["exit_key"],
            "resume_key": config["general"]["resume_key"],
            "auto_settings_key": config["general"]["auto_settings_key"],
            "color_checker_key": config["general"]["color_checker_key"],
        }
        self.routes = {
            "run_pindle": bool(int(config["routes"]["run_pindle"])),
            "run_shenk": bool(int(config["routes"]["run_shenk"])) if "run_shenk" in config["routes"] else False,
        }
        self.char = {
            "type": config["char"]["type"],
            "show_items": config["char"]["show_items"],
            "inventory_screen": config["char"]["inventory_screen"],
            "stand_still": config["char"]["stand_still"],
            "num_loot_columns": int(config["char"]["num_loot_columns"]),
            "take_health_potion": float(config["char"]["take_health_potion"]),
            "take_mana_potion": float(config["char"]["take_mana_potion"]),
            "heal_merc": float(config["char"]["heal_merc"]),
            "chicken": float(config["char"]["chicken"]),
            "tp": config["char"]["tp"],
            "show_belt": config["char"]["show_belt"],
            "potion1": config["char"]["potion1"],
            "potion2": config["char"]["potion2"],
            "potion3": config["char"]["potion3"],
            "potion4": config["char"]["potion4"],
            "cta_available": bool(int(config["char"]["cta_available"])),
            "weapon_switch": config["char"]["weapon_switch"],
            "battle_orders": config["char"]["battle_orders"],
            "battle_command": config["char"]["battle_command"],
            "casting_frames": int(config["char"]["casting_frames"])
        }

        self.sorceress = config["sorceress"]

        self.hammerdin = config["hammerdin"]

        self.items = {}
        for key in config["items"]:
            self.items[key] = bool(int(config["items"][key]))

        self.colors = {}
        for key in ui_config["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in ui_config["colors"][key].split(",")]), 2)

        self.ui_pos = {}
        for key in ui_config["ui_pos_1920_1080"]:
            self.ui_pos[key] = int(ui_config["ui_pos_1920_1080"][key])

if __name__ == "__main__":
    config = Config()
