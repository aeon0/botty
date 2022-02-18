import keyboard
import os
import numpy as np
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from config import Config
from screen import grab, convert_screen_to_monitor
from item import ItemFinder
from template_finder import TemplateFinder, TemplateMatch
from dataclasses import dataclass
from messages import Messenger
from game_stats import GameStats

messenger = Messenger()
game_stats = GameStats()

@dataclass
class ScreenObject:
    _screen_object = None
    ref: list[str]
    inp_img: np.ndarray = None
    roi: list[float] = None
    time_out: float = 30
    threshold: float = 0.68
    normalize_monitor: bool = False
    best_match: bool = False
    use_grayscale: bool = False

    def __call__(self, cls):
        cls._screen_object = self
        return cls

class ScreenObjects:
    BarAnchor = ScreenObject(
        ref="WINDOW_INGAME_REFERENCE",
        roi="window_ingame_ref",
        threshold=0.8
    )
    WaypointLabel=ScreenObject(
        ref="LABEL_WAYPOINT",
        roi="left_panel_label",
        threshold=0.8
    )
    WaypointTabs=ScreenObject(
        ref=["WP_A1_ACTIVE", "WP_A2_ACTIVE", "WP_A3_ACTIVE", "WP_A4_ACTIVE", "WP_A5_ACTIVE"],
        roi="wp_act_roi",
        threshold=0.8,
        best_match=True
    )
    MercIcon=ScreenObject(
        ref=["MERC_A2", "MERC_A1", "MERC_A5", "MERC_A3"],
        roi="merc_icon",
        threshold=0.9
    )
    PlayBtn=ScreenObject(
        ref=["PLAY_BTN", "PLAY_BTN_GRAY"],
        roi="play_btn",
        best_match=True
    )
    MainMenu=ScreenObject(
        ref=["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK"],
        roi="main_menu_top_left"
    )
    Loading=ScreenObject(
        ref=["LOADING", "CREATING_GAME"],
        roi="difficulty_select",
        threshold=0.9
    )
    Normal=ScreenObject(
        ref=["NORMAL_BTN"],
        roi="difficulty_select",
        threshold=0.9
    )
    Nightmare=ScreenObject(
        ref=["NIGHTMARE_BTN"],
        roi="difficulty_select",
        threshold=0.9
    )
    Hell=ScreenObject(
        ref=["HELL_BTN"],
        roi="difficulty_select",
        threshold=0.9
    )
    CubeInventory=ScreenObject(
        ref=["HORADRIC_CUBE"],
        roi="left_inventory",
        threshold=0.8
    )
    CubeOpened=ScreenObject(
        ref=["CUBE_TRANSMUTE_BTN"],
        roi="cube_btn_roi",
        threshold=0.8
    )
    OnlineStatus=ScreenObject(
        ref=["CHARACTER_STATE_ONLINE", "CHARACTER_STATE_OFFLINE"],
        roi="character_online_status",
        best_match=True
    )
    SelectedCharacter=ScreenObject(
        ref=["CHARACTER_ACTIVE"],
        roi="character_select",
        threshold=0.8
    )
    ServerError=ScreenObject(
        ref=["SERVER_ISSUES"]
    )
    SaveAndExit=ScreenObject(
        ref=["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"],
        roi="save_and_exit",
        threshold=0.85
    )
    NeedRepair=ScreenObject(
        ref="REPAIR_NEEDED",
        roi="repair_needed"
    )
    ItemPickupText=ScreenObject(
        ref=["ITEM_PICKUP_ENABLED","ITEM_PICKUP_DISABLED"],
        roi="item_pickup_text",
        best_match=True
    )
    ShrineArea=ScreenObject(
        ref=["SHRINE", "HIDDEN_STASH", "SKULL_PILE"],
        roi="shrine_check",
        threshold=0.8
    )
    TownPortal=ScreenObject(
        ref="BLUE_PORTAL",
        threshold=0.66,
        roi="tp_search",
        normalize_monitor=True
    )
    TownPortalReduced=ScreenObject(
        ref="BLUE_PORTAL",
        threshold=0.66,
        roi="reduce_to_center",
        normalize_monitor=True
    )
    GoldBtnInventory=ScreenObject(
        ref="INVENTORY_GOLD_BTN",
        roi="gold_btn",
        normalize_monitor=True,
        use_grayscale=True
    )
    GoldBtnStash=ScreenObject(
        ref="INVENTORY_GOLD_BTN",
        roi="gold_btn_stash",
        normalize_monitor=True,
        use_grayscale=True
    )
    GoldNone=ScreenObject(
        ref="INVENTORY_NO_GOLD",
        roi="inventory_gold",
        threshold=0.83,
        use_grayscale=True
    )
    TownPortalSkill=ScreenObject(
        ref=["TP_ACTIVE", "TP_INACTIVE"],
        roi="skill_right",
        best_match=True,
        threshold=0.79
    )
    RepairBtn=ScreenObject(
        ref="REPAIR_BTN",
        roi="repair_btn",
        normalize_monitor=True,
        use_grayscale=True
    )
    YouHaveDied=ScreenObject(
        ref="YOU_HAVE_DIED",
        roi="death",
        threshold=0.9
    )
    Overburdened=ScreenObject(
        ref=["INVENTORY_FULL_MSG_0", "INVENTORY_FULL_MSG_1"],
        roi="is_overburdened",
        threshold=0.9
    )

def detect_screen_object(screen_object: ScreenObject, img: np.ndarray = None) -> TemplateMatch:
    roi = Config().ui_roi[screen_object.roi] if screen_object.roi else None
    img = grab() if img is None else img
    match = TemplateFinder().search(
        ref = screen_object.ref,
        inp_img = img,
        threshold = screen_object.threshold,
        roi = roi,
        best_match = screen_object.best_match,
        use_grayscale = screen_object.use_grayscale,
        normalize_monitor = screen_object.normalize_monitor)
    if match.valid:
        return match
    return match

def select_screen_object_match(match: TemplateMatch) -> None:
    mouse.move(*convert_screen_to_monitor(match.center))
    wait(0.05, 0.09)
    mouse.click("left")
    wait(0.05, 0.09)

def wait_for_screen_object(screen_object: ScreenObject, time_out: int = None) -> TemplateMatch:
    roi = Config().ui_roi[screen_object.roi] if screen_object.roi else None
    time_out = time_out if time_out else 30
    match = TemplateFinder().search_and_wait(
        ref = screen_object.ref,
        time_out = time_out,
        threshold = screen_object.threshold,
        roi = roi,
        best_match = screen_object.best_match,
        use_grayscale = screen_object.use_grayscale,
        normalize_monitor = screen_object.normalize_monitor)
    if match.valid:
        return match
    return match

def hover_over_screen_object_match(match) -> None:
    mouse.move(*convert_screen_to_monitor(match.center))
    wait(0.2, 0.4)

# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    from ui_components import vendor
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    print("Start")
    from config import Config
    game_stats = GameStats()
    item_finder = ItemFinder()
    vendor.gamble()
