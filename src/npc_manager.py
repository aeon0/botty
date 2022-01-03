import time
import os
from template_finder import TemplateFinder
from config import Config
from screen import Screen
from utils.misc import color_filter, wait
from logger import Logger
import keyboard
from utils.custom_mouse import mouse


class Npc:
    #A1
    KASHYA = "kashya" 
    CHARSI = "charsi"    
    AKARA = "akara" 
    CAIN = "cain"    
    #A2
    FARA = "fara"
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
                "template_group": ["QUAL_FRONT", "QUAL_SIDE", "QUAL_BACK", "QUAL_45", "QUAL_45_2", "QUAL_45_3"]
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
                "template_group": ["MALAH_FRONT", "MALAH_BACK", "MALAH_45", "MALAH_SIDE", "MALAH_SIDE_2"]
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
                "template_group": ["LARZUK_FRONT", "LARZUK_BACK", "LARZUK_SIDE", "LARZUK_SIDE_2", "LARZUK_SIDE_3"]
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
                "template_group": ["FARA_LIGHT_1", "FARA_LIGHT_2", "FARA_LIGHT_3", "FARA_LIGHT_4", "FARA_LIGHT_5", "FARA_LIGHT_6", "FARA_LIGHT_7", "FARA_LIGHT_8", "FARA_LIGHT_9", "FARA_MEDIUM_1", "FARA_MEDIUM_2", "FARA_MEDIUM_3", "FARA_MEDIUM_4", "FARA_MEDIUM_5", "FARA_MEDIUM_6", "FARA_MEDIUM_7", "FARA_DARK_1", "FARA_DARK_2", "FARA_DARK_3", "FARA_DARK_4", "FARA_DARK_5", "FARA_DARK_6", "FARA_DARK_7"]
            },
            # Currently just nametag added to avoid having him focused when wanting to talk to tyrael or qual
            #added in the ability to ID items at cain.
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
                "template_group": ["JAMELLA_FRONT", "JAMELLA_BACK", "JAMELLA_SIDE", "JAMELLA_SIDE_2", "JAMELLA_SIDE_3"]
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
                "template_group": ["HALBU_FRONT", "HALBU_BACK", "HALBU_SIDE", "HALBU_SIDE_2"]
            },            
            #A1
            Npc.AKARA: {
                "name_tag_white": color_filter(self._template_finder.get_template("AKARA_NAME_TAG_WHITE"), self._config.colors["white"])[1],
                "name_tag_gold": color_filter(self._template_finder.get_template("AKARA_NAME_TAG_GOLD"), self._config.colors["gold"])[1],
                "action_btns": {
                    "trade": {
                        "white": color_filter(self._template_finder.get_template("TRADE"), self._config.colors["white"])[1],
                        "blue": color_filter(self._template_finder.get_template("TRADE_BLUE"), self._config.colors["blue"])[1],
                    }
                },
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
        # Check if we by chance have cain selected while pathing
        _, filtered_inp_g = color_filter(self._screen.grab(), self._config.colors["gold"])
        if self._template_finder.search(self._npcs[Npc.CAIN]["name_tag_gold"], filtered_inp_g, 0.9, roi=roi).valid:
            keyboard.send("esc")
        # Search for npc name tags by hovering to all template locations that are found
        start = time.time()
        while (time.time() - start) < 35:
            img = self._screen.grab()
            results = []
            for key in self._npcs[npc_key]["template_group"]:
                res = self._template_finder.search(key, img, threshold=0.35, roi=roi, normalize_monitor=True)
                if res.valid:
                    results.append({"pos": res.position, "score": res.score})
            results = sorted(results, key=lambda r: r["score"], reverse=True)

            for result in results:
                mouse.move(*result["pos"], randomize=3, delay_factor=[0.9, 1.5])
                wait(0.2, 0.3)
                _, filtered_inp_w = color_filter(self._screen.grab(), self._config.colors["white"])
                _, filtered_inp_g = color_filter(self._screen.grab(), self._config.colors["gold"])
                res_w = self._template_finder.search(self._npcs[npc_key]["name_tag_white"], filtered_inp_w, 0.9, roi=roi).valid
                res_g = self._template_finder.search(self._npcs[npc_key]["name_tag_gold"], filtered_inp_g, 0.9, roi=roi).valid
                if res_w:
                    mouse.click(button="left")
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
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    npc_manager = NpcManager(screen, template_finder)
    npc_manager.open_npc_menu(Npc.TYRAEL)
    # npc_manager.press_npc_btn(Npc.ORMUS, "trade")
