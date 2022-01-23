import configparser
import threading
import numpy as np
import os
import re
from dataclasses import dataclass
from logger import Logger

config_lock = threading.Lock()


@dataclass
class ItemProps:
    pickit_type: int = 0
    include: list[str] = None
    exclude: list[str] = None
    include_type: str = "OR"
    exclude_type: str = "OR"

class Config:
    data_loaded = False
    # all configparser objects
    _config = None
    _game_config = None
    _pickit_config = None
    _shop_config = None
    _custom = None


    def __init__(self):
        with config_lock:
            if not Config.data_loaded:
                Config.data_loaded = True
                Config.load_data()

    @staticmethod
    def _select_val(section: str, key: str = None):
        if section in Config._custom and key in Config._custom[section]:
            return Config._custom[section][key]
        elif section in Config._config:
            return Config._config[section][key]
        elif section in Config._pickit_config:
            return Config._pickit_config[section][key]
        elif section in Config._shop_config:
            return Config._shop_config[section][key]
        else:
            return Config._game_config[section][key]

    @staticmethod
    def parse_item_config_string(key: str = None) -> ItemProps:
        item_props = ItemProps()
        # split string by commas NOT contained within parentheses
        item_string_as_list = re.split(r',\s*(?![^()]*\))', Config._select_val("items", key).upper())
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

    @staticmethod
    def turn_off_goldpickup():
        with config_lock:
            Config.char["stash_gold"] = False
            Config.items["misc_gold"].pickit_type = 0

    @staticmethod
    def load_data():
        Logger.info("Loading Config Data")
        Config._config = configparser.ConfigParser()
        Config._config.read('config/params.ini')
        Config._game_config = configparser.ConfigParser()
        Config._game_config.read('config/game.ini')
        Config._pickit_config = configparser.ConfigParser()
        Config._pickit_config.read('config/pickit.ini')
        Config._shop_config = configparser.ConfigParser()
        Config._shop_config.read('config/shop.ini')
        Config._custom = configparser.ConfigParser()
        if os.environ.get('RUN_ENV') != "test" and os.path.exists('config/custom.ini'):
            Config._custom.read('config/custom.ini')

        Config.general = {
            "saved_games_folder": Config._select_val("general", "saved_games_folder"),
            "name": Config._select_val("general", "name"),
            "monitor": int(Config._select_val("general", "monitor")),
            "max_game_length_s": float(Config._select_val("general", "max_game_length_s")),
            "exit_key": Config._select_val("general", "exit_key"),
            "resume_key": Config._select_val("general", "resume_key"),
            "auto_settings_key": Config._select_val("general", "auto_settings_key"),
            "restore_settings_from_backup_key": Config._select_val("general", "restore_settings_from_backup_key"),
            "settings_backup_key": Config._select_val("general", "settings_backup_key"),
            "graphic_debugger_key": Config._select_val("general", "graphic_debugger_key"),
            "logg_lvl": Config._select_val("general", "logg_lvl"),
            "randomize_runs": bool(int(Config._select_val("general", "randomize_runs"))),
            "difficulty": Config._select_val("general", "difficulty"),
            "message_api_type": Config._select_val("general", "message_api_type"),
            "custom_message_hook": Config._select_val("general", "custom_message_hook"),
            "discord_status_count": False if not Config._select_val("general", "discord_status_count") else int(Config._select_val("general", "discord_status_count")),
            "discord_status_condensed": bool(int(Config._select_val("general", "discord_status_condensed"))),
            "info_screenshots": bool(int(Config._select_val("general", "info_screenshots"))),
            "loot_screenshots": bool(int(Config._select_val("general", "loot_screenshots"))),
            "d2r_path": Config._select_val("general", "d2r_path"),
            "restart_d2r_when_stuck": bool(int(Config._select_val("general", "restart_d2r_when_stuck"))),
            "find_window_via_win32_api": bool(int(Config._select_val("general", "find_window_via_win32_api")))
        }

        # Added for dclone ip hunting
        Config.dclone = {
            "region_ips": Config._select_val("dclone", "region_ips"),
            "dclone_hotip": Config._select_val("dclone", "dclone_hotip"),
        }

        Config.routes = {}
        order_str = Config._select_val("routes", "order").replace("run_eldritch", "run_shenk")
        Config.routes_order = [x.strip() for x in order_str.split(",")]
        del Config._config["routes"]["order"]
        for key in Config._config["routes"]:
            Config.routes[key] = bool(int(Config._select_val("routes", key)))

        Config.char = {
            "type": Config._select_val("char", "type"),
            "show_items": Config._select_val("char", "show_items"),
            "inventory_screen": Config._select_val("char", "inventory_screen"),
            "stand_still": Config._select_val("char", "stand_still"),
            "force_move": Config._select_val("char", "force_move"),
            "num_loot_columns": int(Config._select_val("char", "num_loot_columns")),
            "take_health_potion": float(Config._select_val("char", "take_health_potion")),
            "take_mana_potion": float(Config._select_val("char", "take_mana_potion")),
            "take_rejuv_potion_health": float(Config._select_val("char", "take_rejuv_potion_health")),
            "take_rejuv_potion_mana": float(Config._select_val("char", "take_rejuv_potion_mana")),
            "heal_merc": float(Config._select_val("char", "heal_merc")),
            "heal_rejuv_merc": float(Config._select_val("char", "heal_rejuv_merc")),
            "chicken": float(Config._select_val("char", "chicken")),
            "merc_chicken": float(Config._select_val("char", "merc_chicken")),
            "tp": Config._select_val("char", "tp"),
            "belt_rows": int(Config._select_val("char", "belt_rows")),
            "show_belt": Config._select_val("char", "show_belt"),
            "potion1": Config._select_val("char", "potion1"),
            "potion2": Config._select_val("char", "potion2"),
            "potion3": Config._select_val("char", "potion3"),
            "potion4": Config._select_val("char", "potion4"),
            "belt_rejuv_columns": int(Config._select_val("char", "belt_rejuv_columns")),
            "belt_hp_columns": int(Config._select_val("char", "belt_hp_columns")),
            "belt_mp_columns": int(Config._select_val("char", "belt_mp_columns")),
            "stash_gold": bool(int(Config._select_val("char", "stash_gold"))),
            "gold_trav_only": bool(int(Config._select_val("char", "gold_trav_only"))),
            "use_merc": bool(int(Config._select_val("char", "use_merc"))),
            "id_items": bool(int(Config._select_val("char", "id_items"))),
            "sell_items": bool(int(Config._select_val("char", "sell_items"))),
            "open_chests": bool(int(Config._select_val("char", "open_chests"))),
            "fill_shared_stash_first": bool(int(Config._select_val("char", "fill_shared_stash_first"))),
            "pre_buff_every_run": bool(int(Config._select_val("char", "pre_buff_every_run"))),
            "cta_available": bool(int(Config._select_val("char", "cta_available"))),
            "weapon_switch": Config._select_val("char", "weapon_switch"),
            "battle_orders": Config._select_val("char", "battle_orders"),
            "battle_command": Config._select_val("char", "battle_command"),
            "casting_frames": int(Config._select_val("char", "casting_frames")),
            "atk_len_arc": float(Config._select_val("char", "atk_len_arc")),
            "atk_len_trav": float(Config._select_val("char", "atk_len_trav")),
            "atk_len_pindle": float(Config._select_val("char", "atk_len_pindle")),
            "atk_len_eldritch": float(Config._select_val("char", "atk_len_eldritch")),
            "atk_len_shenk": float(Config._select_val("char", "atk_len_shenk")),
            "atk_len_nihlatak": float(Config._select_val("char", "atk_len_nihlatak")),
            "atk_len_diablo_vizier": float(Config._select_val("char", "atk_len_diablo_vizier")),
            "atk_len_diablo_deseis": float(Config._select_val("char", "atk_len_diablo_deseis")),
            "atk_len_diablo_infector": float(Config._select_val("char", "atk_len_diablo_infector")),
            "atk_len_diablo": float(Config._select_val("char", "atk_len_diablo")),
            "atk_len_cs_trashmobs": float(Config._select_val("char", "atk_len_cs_trashmobs")),
            "kill_cs_trash": float(Config._select_val("char", "kill_cs_trash")),
            "always_repair": bool(int(Config._select_val("char", "always_repair"))),
        }

        # Sorc base config
        sorc_base_cfg = dict(Config._config["sorceress"])
        if "sorceress" in Config._custom:
            sorc_base_cfg.update(dict(Config._custom["sorceress"]))
        # blizz sorc
        Config.blizz_sorc = dict(Config._config["blizz_sorc"])
        if "blizz_sorc" in Config._custom:
            Config.blizz_sorc.update(dict(Config._custom["blizz_sorc"]))
        Config.blizz_sorc.update(sorc_base_cfg)
        # light sorc
        Config.light_sorc = dict(Config._config["light_sorc"])
        if "light_sorc" in Config._custom:
            Config.light_sorc.update(dict(Config._custom["light_sorc"]))
        Config.light_sorc.update(sorc_base_cfg)
        # nova sorc
        Config.nova_sorc = dict(Config._config["nova_sorc"])
        if "nova_sorc" in Config._custom:
            Config.nova_sorc.update(dict(Config._custom["nova_sorc"]))
        Config.nova_sorc.update(sorc_base_cfg)

        # Palandin config
        Config.hammerdin = Config._config["hammerdin"]
        if "hammerdin" in Config._custom:
            Config.hammerdin.update(Config._custom["hammerdin"])

        # Assasin config
        Config.trapsin = Config._config["trapsin"]
        if "trapsin" in Config._custom:
            Config.trapsin.update(Config._custom["trapsin"])

        # Barbarian config
        Config.barbarian = Config._config["barbarian"]
        if "barbarian" in Config._custom:
            Config.barbarian.update(Config._custom["barbarian"])
        Config.barbarian = dict(Config.barbarian)
        Config.barbarian["cry_frequency"] = float(Config.barbarian["cry_frequency"])

        # Basic config
        Config.basic = Config._config["basic"]
        if "basic" in Config._custom:
            Config.basic.update(Config._custom["basic"])

        # Basic Ranged config
        Config.basic_ranged = Config._config["basic_ranged"]
        if "basic_ranged" in Config._custom:
            Config.basic_ranged.update(Config._custom["basic_ranged"])

        # Necro config
        Config.necro = Config._config["necro"]
        if "necro" in Config._custom:
            Config.necro.update(Config._custom["necro"])

        Config.advanced_options = {
            "pathing_delay_factor": min(max(int(Config._select_val("advanced_options", "pathing_delay_factor")), 1), 10),
            "message_headers": Config._select_val("advanced_options", "message_headers"),
            "message_body_template": Config._select_val("advanced_options", "message_body_template"),
            "message_highlight": bool(int(Config._select_val("advanced_options", "message_highlight"))),
            "d2r_windows_always_on_top": bool(int(Config._select_val("advanced_options", "d2r_windows_always_on_top"))),
            "graphic_debugger_layer_creator": bool(int(Config._select_val("advanced_options", "graphic_debugger_layer_creator"))),
        }

        Config.items = {}
        for key in Config._pickit_config["items"]:
            try:
                Config.items[key] = Config.parse_item_config_string(key)
                if Config.items[key].pickit_type and not os.path.exists(f"./assets/items/{key}.png"):
                    print(f"Warning: You activated {key} in pickit, but there is no img available in assets/items")
            except ValueError as e:
                print(f"Error with pickit config: {key} ({e})")

        Config.colors = {}
        for key in Config._game_config["colors"]:
            Config.colors[key] = np.split(np.array([int(x) for x in Config._select_val("colors", key).split(",")]), 2)

        Config.ui_pos = {}
        for key in Config._game_config["ui_pos"]:
            Config.ui_pos[key] = int(Config._select_val("ui_pos", key))

        Config.ui_roi = {}
        for key in Config._game_config["ui_roi"]:
            Config.ui_roi[key] = np.array([int(x) for x in Config._select_val("ui_roi", key).split(",")])

        Config.path = {}
        for key in Config._game_config["path"]:
            Config.path[key] = np.reshape(np.array([int(x) for x in Config._select_val("path", key).split(",")]), (-1, 2))

        Config.shop = {
            "shop_trap_claws": bool(int(Config._select_val("claws", "shop_trap_claws"))),
            "shop_melee_claws": bool(int(Config._select_val("claws", "shop_melee_claws"))),
            "shop_3_skills_ias_gloves": bool(int(Config._select_val("gloves", "shop_3_skills_ias_gloves"))),
            "shop_2_skills_ias_gloves": bool(int(Config._select_val("gloves", "shop_2_skills_ias_gloves"))),
            "trap_min_score": int(Config._select_val("claws", "trap_min_score")),
            "melee_min_score": int(Config._select_val("claws", "melee_min_score")),
            "shop_hammerdin_scepters": bool(int(Config._select_val("scepters", "shop_hammerdin_scepters"))),
            "speed_factor": float(Config._select_val("scepters", "speed_factor")),
            "apply_pather_adjustment": bool(int(Config._select_val("scepters", "apply_pather_adjustment"))),
        }


if __name__ == "__main__":
    from copy import deepcopy
    config = Config()

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
