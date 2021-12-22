import configparser
import numpy as np
import os
import re
from dataclasses import dataclass
from logger import Logger

@dataclass
class ItemProps:
    pickit_type: int = 0
    include: list[str] = None
    exclude: list[str] = None
    include_type: str = "OR"
    exclude_type: str = "OR"

class Config:
    def _select_val(self, section: str, key: str = None):
        if section in self._custom and key in self._custom[section]:
            return self._custom[section][key]
        elif section in self._config:
            return self._config[section][key]
        elif section in self._pickit_config:
            return self._pickit_config[section][key]
        elif section in self._shop_config:
            return self._shop_config[section][key]
        else:
            return self._game_config[section][key]

    def __init__(self, print_warnings: bool = False):
        # print_warnings, what a hack... here it is, not making the effort
        # passing a single config instance through bites me in the ass
        self._print_warnings = print_warnings
        self._config = configparser.ConfigParser()
        self._config.read('config/params.ini')
        self._game_config = configparser.ConfigParser()
        self._game_config.read('config/game.ini')
        self._pickit_config = configparser.ConfigParser()
        self._pickit_config.read('config/pickit.ini')
        self._shop_config = configparser.ConfigParser()
        self._shop_config.read('config/shop.ini')
        self._custom = configparser.ConfigParser()
        if os.environ.get('RUN_ENV') != "test" and os.path.exists('config/custom.ini'):
            self._custom.read('config/custom.ini')

        self.general = {
            "saved_games_folder": self._select_val("general", "saved_games_folder"),
            "name": self._select_val("general", "name"),
            "monitor": int(self._select_val("general", "monitor")),
            "max_game_length_s": float(self._select_val("general", "max_game_length_s")),
            "exit_key": self._select_val("general", "exit_key"),
            "resume_key": self._select_val("general", "resume_key"),
            "auto_settings_key": self._select_val("general", "auto_settings_key"),
            "graphic_debugger_key": self._select_val("general", "graphic_debugger_key"),
            "logg_lvl": self._select_val("general", "logg_lvl"),
            "randomize_runs": bool(int(self._select_val("general", "randomize_runs"))),
            "difficulty": self._select_val("general", "difficulty"),
            "custom_message_hook": self._select_val("general", "custom_message_hook"),
            "discord_status_count": False if not self._select_val("general", "discord_status_count") else int(self._select_val("general", "discord_status_count")),
            "discord_status_condensed": bool(int(self._select_val("general", "discord_status_condensed"))),
            "info_screenshots": bool(int(self._select_val("general", "info_screenshots"))),
            "loot_screenshots": bool(int(self._select_val("general", "loot_screenshots"))),
        }

        # Added for dclone ip hunting
        self.dclone = {
            "region_ips": self._select_val("dclone", "region_ips"),
            "dclone_hotip": self._select_val("dclone", "dclone_hotip"),
        }

        self.routes = {}
        order_str = self._select_val("routes", "order").replace("run_eldritch", "run_shenk")
        self.routes_order = [x.strip() for x in order_str.split(",")]
        del self._config["routes"]["order"]
        for key in self._config["routes"]:
            self.routes[key] = bool(int(self._select_val("routes", key)))

        self.char = {
            "type": self._select_val("char", "type"),
            "show_items": self._select_val("char", "show_items"),
            "inventory_screen": self._select_val("char", "inventory_screen"),
            "stand_still": self._select_val("char", "stand_still"),
            "force_move": self._select_val("char", "force_move"),
            "num_loot_columns": int(self._select_val("char", "num_loot_columns")),
            "take_health_potion": float(self._select_val("char", "take_health_potion")),
            "take_mana_potion": float(self._select_val("char", "take_mana_potion")),
            "take_rejuv_potion_health": float(self._select_val("char", "take_rejuv_potion_health")),
            "take_rejuv_potion_mana": float(self._select_val("char", "take_rejuv_potion_mana")),
            "heal_merc": float(self._select_val("char", "heal_merc")),
            "heal_rejuv_merc": float(self._select_val("char", "heal_rejuv_merc")),
            "chicken": float(self._select_val("char", "chicken")),
            "merc_chicken": float(self._select_val("char", "merc_chicken")),
            "tp": self._select_val("char", "tp"),
            "belt_rows": int(self._select_val("char", "belt_rows")),
            "show_belt": self._select_val("char", "show_belt"),
            "potion1": self._select_val("char", "potion1"),
            "potion2": self._select_val("char", "potion2"),
            "potion3": self._select_val("char", "potion3"),
            "potion4": self._select_val("char", "potion4"),
            "belt_rejuv_columns": int(self._select_val("char", "belt_rejuv_columns")),
            "belt_hp_columns": int(self._select_val("char", "belt_hp_columns")),
            "belt_mp_columns": int(self._select_val("char", "belt_mp_columns")),
            "stash_gold": bool(int(self._select_val("char", "stash_gold"))),
            "gold_trav_only": bool(int(self._select_val("char", "gold_trav_only"))),
            "use_merc": bool(int(self._select_val("char", "use_merc"))),
            "pre_buff_every_run": bool(int(self._select_val("char", "pre_buff_every_run"))),
            "cta_available": bool(int(self._select_val("char", "cta_available"))),
            "weapon_switch": self._select_val("char", "weapon_switch"),
            "battle_orders": self._select_val("char", "battle_orders"),
            "battle_command": self._select_val("char", "battle_command"),
            "casting_frames": int(self._select_val("char", "casting_frames")),
            "atk_len_trav": float(self._select_val("char", "atk_len_trav")),
            "atk_len_pindle": float(self._select_val("char", "atk_len_pindle")),
            "atk_len_eldritch": float(self._select_val("char", "atk_len_eldritch")),
            "atk_len_shenk": float(self._select_val("char", "atk_len_shenk")),
            "atk_len_nihlatak": float(self._select_val("char", "atk_len_nihlatak")),
        }

        # Sorc base config
        sorc_base_cfg = dict(self._config["sorceress"])
        if "sorceress" in self._custom:
            sorc_base_cfg.update(dict(self._custom["sorceress"]))
        # blizz sorc
        self.blizz_sorc = dict(self._config["blizz_sorc"])
        if "blizz_sorc" in self._custom:
            self.blizz_sorc.update(dict(self._custom["blizz_sorc"]))
        self.blizz_sorc.update(sorc_base_cfg)
        # light sorc
        self.light_sorc = dict(self._config["light_sorc"])
        if "light_sorc" in self._custom:
            self.light_sorc.update(dict(self._custom["light_sorc"]))
        self.light_sorc.update(sorc_base_cfg)

        # Palandin config
        self.hammerdin = self._config["hammerdin"]
        if "hammerdin" in self._custom:
            self.hammerdin.update(self._custom["hammerdin"])

        # Assasin config
        self.trapsin = self._config["trapsin"]
        if "trapsin" in self._custom:
            self.trapsin.update(self._custom["trapsin"])

        # Barbarian config
        self.barbarian = self._config["barbarian"]
        if "barbarian" in self._custom:
            self.barbarian.update(self._custom["barbarian"])

        self.advanced_options = {
            "pathing_delay_factor": min(max(int(self._select_val("advanced_options", "pathing_delay_factor")), 1), 10),
            "message_headers": self._select_val("advanced_options", "message_headers"),
            "message_body_template": self._select_val("advanced_options", "message_body_template"),
            "message_highlight": bool(int(self._select_val("advanced_options", "message_highlight"))),
        }

        self.items = {}
        for key in self._pickit_config["items"]:
            self.items[key] = self.parse_item_config_string(key)
            if self.items[key].pickit_type and not os.path.exists(f"./assets/items/{key}.png") and self._print_warnings:
                print(f"Warning: You activated {key} in pickit, but there is no img available in assets/items")

        self.colors = {}
        for key in self._game_config["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)

        self.ui_pos = {}
        for key in self._game_config["ui_pos"]:
            self.ui_pos[key] = int(self._select_val("ui_pos", key))

        self.ui_roi = {}
        for key in self._game_config["ui_roi"]:
            self.ui_roi[key] = np.array([int(x) for x in self._select_val("ui_roi", key).split(",")])

        self.path = {}
        for key in self._game_config["path"]:
            self.path[key] = np.reshape(np.array([int(x) for x in self._select_val("path", key).split(",")]), (-1, 2))

        self.shop = {
            "shop_trap_claws": bool(int(self._select_val("claws", "shop_trap_claws"))),
            "shop_melee_claws": bool(int(self._select_val("claws", "shop_melee_claws"))),
            "shop_3_skills_ias_gloves": bool(int(self._select_val("gloves", "shop_3_skills_ias_gloves"))),
            "shop_2_skills_ias_gloves": bool(int(self._select_val("gloves", "shop_2_skills_ias_gloves"))),
            "trap_min_score": int(self._select_val("claws", "trap_min_score")),
            "melee_min_score": int(self._select_val("claws", "melee_min_score")),
        }

    def parse_item_config_string(self, key: str = None) -> ItemProps:
        item_props = ItemProps()
        # split string by commas NOT contained within parentheses
        item_string_as_list = re.split(r',\s*(?![^()]*\))', self._select_val("items", key).upper())
        trim_strs=["AND(", "OR(", "(", ")", " "]
        clean_string = [re.sub(r'|'.join(map(re.escape, trim_strs)), '', x).strip() for x in item_string_as_list]
        item_props.pickit_type = int(clean_string[0])
        try:
            item_props.include = clean_string[1].split(',') if clean_string[1] else None
            item_props.include_type = "AND" if "AND" in item_string_as_list[1] else "OR"
        except IndexError as error:
            pass
        except Exception as exception:
            Logger.error(f"Item parsing error: {exception}")
        try:
            item_props.exclude = clean_string[2].split(',') if clean_string[2] else None
            item_props.exclude_type = "AND" if "AND" in item_string_as_list[2] else "OR"
        except IndexError as error:
            pass
        except Exception as exception:
            Logger.error(f"Item parsing error: {exception}")
        return item_props

if __name__ == "__main__":
    config = Config(print_warnings=True)

    # Check if any added items miss templates
    for k in config.items:
        if not os.path.exists(f"./assets/items/{k}.png"):
            print(f"Template not found: {k}")

    # Check if any item templates miss a config
    for filename in os.listdir(f'assets/items'):
        filename = filename.lower()
        if filename.endswith('.png'):
            item_name = filename[:-4]
            blacklist_item = item_name.startswith("bl__")
            if item_name not in config.items and not blacklist_item:
                print(f"Config not found for: " + filename)
