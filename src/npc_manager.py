import time
import os
from template_finder import TemplateFinder
from config import Config
from screen import Screen
from utils.misc import color_filter, wait
from logger import Logger
import keyboard
from utils.custom_mouse import mouse
from math import sqrt


class Npc:
    #A1
    KASHYA = "kashya"
    CHARSI = "charsi"
    AKARA = "akara"
    CAIN = "cain"
    #A2
    FARA = "fara"
    DROGNAN = "droganan"
    LYSANDER = "lysander"
    #A3
    ORMUS = "ormus"
    #A4
    TYRAEL = "tyrael"
    JAMELLA = "jamella"
    HALBU = "halbu"
    #A5
    QUAL_KEHK = "qual_kehk"
    MALAH = "malah"
    LARZUK = "larzuk"
    ANYA = "anya"

class NpcManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._npcs = {
            Npc.QUAL_KEHK: {
                "name_tag_white": color_filter(self._template_finder.get_template("QUAL_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("QUAL_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "resurrect": {
                        "white": color_filter(self._template_finder.get_template("RESURRECT"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("RESURRECT_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["QUAL_0", "QUAL_45", "QUAL_45_B", "QUAL_90", "QUAL_135", "QUAL_135_B", "QUAL_135_C", "QUAL_180", "QUAL_180_B", "QUAL_225", "QUAL_225_B", "QUAL_270", "QUAL_315"],
                "roi": [225, 57, (850-225), (442-57)],
                "poses": [[350, 140], [310, 268], [385, 341], [481, 196], [502, 212], [771, 254]]
            },
            Npc.MALAH: {
                "name_tag_white": color_filter(self._template_finder.get_template("MALAH_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("MALAH_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["MALAH_FRONT", "MALAH_BACK", "MALAH_45", "MALAH_SIDE", "MALAH_SIDE_2"],
                "roi": [383, 193, (762-383), (550-193)],
                "poses": [[445, 485], [526, 473], [602, 381], [623, 368], [641, 323], [605, 300], [622, 272], [638, 284], [677, 308], [710, 288]]
            },
            Npc.LARZUK: {
                "name_tag_white": color_filter(self._template_finder.get_template("LARZUK_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("LARZUK_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade_repair": {
                        "white": color_filter(self._template_finder.get_template("TRADE_REPAIR"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_REPAIR_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [570, 70, (1038-570), (290-70)],
                "template_group": ["LARZUK_FRONT", "LARZUK_BACK", "LARZUK_SIDE", "LARZUK_SIDE_2", "LARZUK_SIDE_3"],
                "poses": [[733, 192], [911, 143]]
            },
            Npc.ANYA: {
                "name_tag_white": color_filter(self._template_finder.get_template("ANYA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("ANYA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["ANYA_FRONT", "ANYA_BACK", "ANYA_SIDE"]
            },
            Npc.TYRAEL: {
                "name_tag_white": color_filter(self._template_finder.get_template("TYRAEL_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("TYRAEL_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "resurrect": {
                        "white": color_filter(self._template_finder.get_template("RESURRECT"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("RESURRECT_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [569, 86, (852-569), (357-86)],
                "template_group": ["TYRAEL_1", "TYRAEL_2"]
            },
            Npc.ORMUS: {
                "name_tag_white": color_filter(self._template_finder.get_template("ORMUS_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("ORMUS_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [444, 13, (816-444), (331-13)],
                "poses": [[526, 131], [602, 192], [698, 218], [756, 188]],
                "template_group": ["ORMUS_0", "ORMUS_1", "ORMUS_2", "ORMUS_3", "ORMUS_4", "ORMUS_5"]
            },
            Npc.FARA: {
                "name_tag_white": color_filter(self._template_finder.get_template("FARA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("FARA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade_repair": {
                        "white": color_filter(self._template_finder.get_template("TRADE_REPAIR"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_REPAIR_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [333, 104, (682-333), (343-104)],
                "poses": [[406, 188], [550, 243], [620, 174]],
                "template_group": ["FARA_LIGHT_1", "FARA_LIGHT_2", "FARA_LIGHT_3", "FARA_LIGHT_4", "FARA_LIGHT_5", "FARA_LIGHT_6", "FARA_LIGHT_7", "FARA_LIGHT_8", "FARA_LIGHT_9", "FARA_MEDIUM_1", "FARA_MEDIUM_2", "FARA_MEDIUM_3", "FARA_MEDIUM_4", "FARA_MEDIUM_5", "FARA_MEDIUM_6", "FARA_MEDIUM_7", "FARA_DARK_1", "FARA_DARK_2", "FARA_DARK_3", "FARA_DARK_4", "FARA_DARK_5", "FARA_DARK_6", "FARA_DARK_7"]
            },
            Npc.DROGNAN: {
                "name_tag_white": color_filter(self._template_finder.get_template("DROGNAN_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("DROGNAN_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["DROGNAN_FRONT", "DROGNAN_LEFT", "DROGNAN_RIGHT_SIDE"]
            },
            Npc.LYSANDER: {
                "name_tag_white": color_filter(self._template_finder.get_template("LYSANDER_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("LYSANDER_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["LYSANDER_FRONT", "LYSANDER_BACK", "LYSANDER_SIDE", "LYSANDER_SIDE_2"]
            },              
            Npc.CAIN: {
                "name_tag_white": color_filter(self._template_finder.get_template("CAIN_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("CAIN_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "identify": {
                        "white": color_filter(self._template_finder.get_template("IDENTIFY"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("IDENTIFY_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["CAIN_0", "CAIN_1", "CAIN_2", "CAIN_3"]
            },
            Npc.JAMELLA: {
                "name_tag_white": color_filter(self._template_finder.get_template("JAMELLA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("JAMELLA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [337, 188, (733-337), (622-188)],
                "poses": [[422, 398], [425, 513], [586, 494], [656, 372], [563, 348]],
                "template_group": ["JAMELLA_FRONT", "JAMELLA_BACK", "JAMELLA_SIDE", "JAMELLA_SIDE_2", "JAMELLA_SIDE_3", "JAMELLA_DRAWING"]
            },
            Npc.HALBU: {
                "name_tag_white": color_filter(self._template_finder.get_template("HALBU_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("HALBU_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade_repair": {
                        "white": color_filter(self._template_finder.get_template("TRADE_REPAIR"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_REPAIR_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [319, 128, (840-319), (403-128)],
                "poses": [[443, 280], [523, 220], [599, 294], [738, 263]],
                "template_group": ["HALBU_FRONT", "HALBU_BACK", "HALBU_SIDE", "HALBU_SIDE_2"]
            },
            Npc.AKARA: {
                "name_tag_white": color_filter(self._template_finder.get_template("AKARA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("AKARA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [603, 176, (1002-603), (478-176)],
                "poses": [[692, 377], [834, 378], [948, 345], [867, 290], [696, 317]],
                "template_group": ["AKARA_FRONT", "AKARA_BACK", "AKARA_SIDE", "AKARA_SIDE_2"]
            },
            Npc.CHARSI: {
                "name_tag_white": color_filter(self._template_finder.get_template("CHARSI_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("CHARSI_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade_repair": {
                        "white": color_filter(self._template_finder.get_template("TRADE_REPAIR"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_REPAIR_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "roi": [249, 76, (543-249), (363-76)],
                "poses": [[331, 227], [368, 284], [484, 174]],
                "template_group": ["CHARSI_FRONT", "CHARSI_BACK", "CHARSI_SIDE", "CHARSI_SIDE_2", "CHARSI_SIDE_3"]
            },
            Npc.KASHYA: {
                "name_tag_white": color_filter(self._template_finder.get_template("KASHYA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("KASHYA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "resurrect": {
                        "white": color_filter(self._template_finder.get_template("RESURRECT"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("RESURRECT_BLUE"), self._config.colors["blue"])[1],
                    }
                },
                "template_group": ["KASHYA_FRONT", "KASHYA_BACK", "KASHYA_SIDE", "KASHYA_SIDE_2"]
            },
        }

    def open_npc_menu(self, npc_key: Npc) -> bool:
        roi = self._config.ui_roi["cut_skill_bar"]
        roi_npc_search = self._config.ui_roi["search_npcs"]
        # Search for npc name tags by hovering to all template locations that are found
        start = time.time()
        attempts = 0
        while (time.time() - start) < 35:
            img = self._screen.grab()
            results = []
            for key in self._npcs[npc_key]["template_group"]:
                if attempts == 0 and "roi" in self._npcs[npc_key] and (time.time() - start) < 6:
                    roi_npc = self._npcs[npc_key]["roi"]
                else:
                    roi_npc = roi_npc_search
                res = self._template_finder.search(key, img, threshold=0.35, roi=roi_npc, normalize_monitor=True)
                if res.valid:
                    is_unique = True
                    for r in results:
                        if (abs(r["pos"][0] - res.position[0]) + abs(r["pos"][1] - res.position[1])) < 22:
                            is_unique = False
                            break
                    if is_unique:
                        min_dist=10000
                        if attempts == 0 and "poses" in self._npcs[npc_key]:
                            # find distance between template match and nearest pose (([x2] - x1)**2 + (y2 - y1)**2)
                            for pose in self._npcs[npc_key]["poses"]:
                                dist = sqrt((res.position[0] - pose[0])**2 + (res.position[1] - pose[1])**2)
                                min_dist = dist if dist < min_dist else min_dist
                        results.append({"pos": res.position, "score": res.score, "combo": min_dist / (res.score**2)})
            # sort by composite of template match score and distance to NPC pose
            results = sorted(results, key=lambda r: r["combo"])

            for result in results:
                mouse.move(*result["pos"], randomize=3, delay_factor=[0.3, 0.5])
                wait(0.2, 0.3)
                _, filtered_inp_w = color_filter(self._screen.grab(), self._config.colors["white"])
                _, filtered_inp_g = color_filter(self._screen.grab(), self._config.colors["gold"])
                res_w = self._template_finder.search(self._npcs[npc_key]["name_tag_white"], filtered_inp_w, 0.9, roi=roi).valid
                res_g = self._template_finder.search(self._npcs[npc_key]["name_tag_gold"], filtered_inp_g, 0.9, roi=roi).valid
                if res_w:
                    mouse.click(button="left")
                    attempts += 1
                    wait(0.7, 1.0)
                    _, filtered_inp = color_filter(self._screen.grab(), self._config.colors["gold"])
                    res = self._template_finder.search(self._npcs[npc_key]["name_tag_gold"], filtered_inp, 0.9, roi=roi).valid
                    if res:
                        return True
                elif res_g:
                    return True
        return False

    def press_npc_btn(self, npc_key: Npc, action_btn_key: str):
        img = self._screen.grab()
        _, filtered_inp_w = color_filter(img, self._config.colors["white"])
        res = self._template_finder.search(
            self._npcs[npc_key]["action_btns"][action_btn_key]["white"],
            filtered_inp_w, 0.85, roi=self._config.ui_roi["cut_skill_bar"],
            normalize_monitor=True
        )
        if not res.valid and "blue" in self._npcs[npc_key]["action_btns"][action_btn_key]:
            # search for highlighted / blue action btn
            _, filtered_inp_b = color_filter(img, self._config.colors["blue"])
            res = self._template_finder.search(
                self._npcs[npc_key]["action_btns"][action_btn_key]["blue"],
                filtered_inp_b, 0.85, roi=self._config.ui_roi["cut_skill_bar"],
                normalize_monitor=True
            )
        if res.valid:
            mouse.move(*res.position, randomize=3, delay_factor=[1.0, 1.5])
            wait(0.2, 0.4)
            mouse.click(button="left")
            wait(0.3, 0.4)
        else:
            Logger.error(f"Could not find {action_btn_key} btn. Should not happen! Continue...")
            keyboard.send("esc")


# Testing: Stand close to Qual-Kehk or Malah and run
if __name__ == "__main__":
    from screen import Screen
    from config import Config
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    screen = Screen()
    template_finder = TemplateFinder(screen)
    npc_manager = NpcManager(screen, template_finder)
    npc_manager.open_npc_menu(Npc.MALAH)
    # npc_manager.press_npc_btn(Npc.ORMUS, "trade")
