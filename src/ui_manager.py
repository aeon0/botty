import keyboard
import os
import numpy as np
import time
import cv2
from functools import cache

from typing import TypeVar, Callable
from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, image_is_equal
from logger import Logger
from config import Config
from screen import convert_abs_to_screen, convert_monitor_to_screen, convert_screen_to_abs, convert_screen_to_monitor, grab, convert_abs_to_monitor
import template_finder
from template_finder import TemplateMatch
from dataclasses import dataclass
from messages import Messenger
from game_stats import GameStats

messenger = Messenger()
game_stats = GameStats()
T = TypeVar('T')

@dataclass
class ScreenObject:
    _screen_object = None
    ref: list[str]
    inp_img: np.ndarray = None
    roi: list[float] = None
    threshold: float = 0.68
    best_match: bool = False
    use_grayscale: bool = False
    color_match: list[np.array] = None
    suppress_debug: bool = False

    def __call__(self, cls):
        cls._screen_object = self
        return cls

class ScreenObjects:
    InGame = ScreenObject(
        ref=["GAMEBAR_ANCHOR", "GAMEBAR_ANCHOR_DARK"],
        roi="gamebar_anchor",
        threshold=0.8,
        best_match=True,
        use_grayscale=True
    )
    WaypointLabel=ScreenObject(
        ref="LABEL_WAYPOINT",
        roi="left_panel_header",
        threshold=0.8,
        use_grayscale=True
    )
    WaypointTabs=ScreenObject(
        ref=["WP_A1_ACTIVE", "WP_A2_ACTIVE", "WP_A3_ACTIVE", "WP_A4_ACTIVE", "WP_A5_ACTIVE"],
        roi="wp_act_roi",
        threshold=0.8,
        best_match=True,
        use_grayscale=True
    )
    MercIcon=ScreenObject(
        ref=["MERC_A2", "MERC_A1", "MERC_A5", "MERC_A3"],
        roi="merc_icon",
        threshold=0.9,
        use_grayscale=True
    )
    PlayBtn=ScreenObject(
        ref=["PLAY_BTN", "PLAY_BTN_GRAY"],
        roi="play_btn",
        best_match=True,
        use_grayscale=True
    )
    MainMenu=ScreenObject(
        ref=["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK"],
        roi="main_menu_top_left",
        best_match=True,
        use_grayscale=True
    )
    Loading=ScreenObject(
        ref=["LOADING", "CREATING_GAME"],
        roi="difficulty_select",
        threshold=0.9,
        use_grayscale=True
    )
    CubeInventory=ScreenObject(
        ref=["HORADRIC_CUBE"],
        roi="left_inventory",
        threshold=0.8,
        use_grayscale=True
    )
    CubeOpened=ScreenObject(
        ref=["CUBE_TRANSMUTE_BTN"],
        roi="cube_btn_roi",
        threshold=0.8,
        use_grayscale=True
    )
    OnlineStatus=ScreenObject(
        ref=["CHARACTER_STATE_ONLINE", "CHARACTER_STATE_OFFLINE"],
        roi="character_online_status",
        best_match=True,
    )
    SelectedCharacter=ScreenObject(
        ref=["CHARACTER_ACTIVE"],
        roi="character_select",
        threshold=0.8,
    )
    ServerError=ScreenObject(
        ref=["SERVER_ISSUES"]
    )
    SaveAndExit=ScreenObject(
        ref=["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"],
        roi="save_and_exit",
        threshold=0.85,
        use_grayscale=True
    )
    NeedRepair=ScreenObject(
        ref="REPAIR_NEEDED",
        roi="repair_needed"
    )
    ItemPickupText=ScreenObject(
        ref=["ITEM_PICKUP_ENABLED","ITEM_PICKUP_DISABLED"],
        roi="chat_line_1",
        best_match=True
    )
    ShrineArea=ScreenObject(
        ref=["SHRINE", "HIDDEN_STASH", "SKULL_PILE"],
        roi="shrine_check",
        threshold=0.8
    )
    TownPortal=ScreenObject(
        ref="BLUE_PORTAL",
        threshold=0.8,
        roi="tp_search"
    )
    TownPortalReduced=ScreenObject(
        ref="BLUE_PORTAL",
        threshold=0.8,
        roi="reduce_to_center"
    )
    GoldBtnInventory=ScreenObject(
        ref="INVENTORY_GOLD_BTN",
        roi="gold_btn",
        use_grayscale=True
    )
    GoldBtnStash=ScreenObject(
        ref="INVENTORY_GOLD_BTN",
        roi="gold_btn_stash"
    )
    GoldBtnVendor=ScreenObject(
        ref="VENDOR_GOLD",
        roi="gold_btn_stash"
    )
    GoldNone=ScreenObject(
        ref="INVENTORY_NO_GOLD",
        roi="inventory_gold",
        threshold=0.83
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
        use_grayscale=True
    )
    YouHaveDied=ScreenObject(
        ref="YOU_HAVE_DIED",
        roi="death",
        threshold=0.9,
        color_match=Config().colors["red"],
        use_grayscale=True
    )
    Overburdened=ScreenObject(
        ref=["INVENTORY_FULL_MSG_0", "INVENTORY_FULL_MSG_1"],
        roi="chat_line_1",
        #color_match=Config().colors["gold"],
        threshold=0.9
    )
    Corpse=ScreenObject(
        ref=["CORPSE", "CORPSE_2", "CORPSE_BARB", "CORPSE_DRU", "CORPSE_NEC", "CORPSE_PAL", "CORPSE_SIN", "CORPSE_SORC", "CORPSE_ZON"],
        roi="corpse",
        threshold=0.8
    )
    BeltExpandable=ScreenObject(
        ref="BELT_EXPANDABLE",
        roi="gamebar_belt_expandable",
        threshold=0.8
    )
    NPCMenu=ScreenObject(
        ref=["TALK", "CANCEL"],
        threshold=0.8,
        use_grayscale=True
    )
    ChatIcon=ScreenObject(
        ref="CHAT_ICON",
        roi="chat_icon",
        threshold=0.8,
        use_grayscale=True
    )
    LeftPanel=ScreenObject(
        ref="CLOSE_PANEL",
        roi="left_panel_header",
        threshold=0.8,
        use_grayscale=True
    )
    RightPanel=ScreenObject(
        ref=["CLOSE_PANEL", "CLOSE_PANEL_2"],
        roi="right_panel_header",
        threshold=0.8,
        use_grayscale=True
    )
    NPCDialogue=ScreenObject(
        ref="NPC_DIALOGUE",
        roi="npc_dialogue",
        threshold=0.8,
        use_grayscale=True
    )
    SkillsExpanded=ScreenObject(
        ref="BIND_SKILL",
        roi="bind_skill",
        threshold=0.8,
        use_grayscale=True
    )
    Unidentified=ScreenObject(
        ref="UNIDENTIFIED",
        threshold=0.8,
        color_match=Config().colors["red"]
    )
    Key=ScreenObject(
        ref="INV_KEY",
        threshold=0.8
    )
    EmptyStashSlot=ScreenObject(
        ref="STASH_EMPTY_SLOT",
        roi="left_inventory",
        threshold=0.8,
    )
    NotEnoughGold=ScreenObject(
        ref="NOT_ENOUGH_GOLD",
        threshold=0.9,
        color_match=Config().colors["red"],
        use_grayscale=True
    )
    QuestSkillBtn=ScreenObject(
        ref="QUEST_SKILL_BTN",
        threshold=0.9,
        use_grayscale=True,
        roi="quest_skill_btn"
    )
    TabIndicator=ScreenObject(
        ref="TAB_INDICATOR",
        roi="tab_indicator",
    )
    DepositBtn=ScreenObject(
        ref=["DEPOSIT_BTN", "DEPOSIT_BTN_BRIGHT"],
        threshold=0.8,
        roi="deposit_btn",
    )
    InventoryBackground=ScreenObject(
        ref="INVENTORY_BG_PATTERN",
        roi="inventory_bg_pattern",
        threshold=0.8,
    )

def detect_screen_object(screen_object: ScreenObject, img: np.ndarray = None) -> TemplateMatch:
    roi = Config().ui_roi[screen_object.roi] if screen_object.roi else None
    img = grab() if img is None else img
    return template_finder.search(
        ref = screen_object.ref,
        inp_img = img,
        threshold = screen_object.threshold,
        roi = roi,
        best_match = screen_object.best_match,
        use_grayscale = screen_object.use_grayscale,
        )

def select_screen_object_match(match: TemplateMatch, delay_factor: tuple[float, float] = (0.9, 1.1)) -> None:
    mouse.move(*match.center_monitor, delay_factor=delay_factor)
    wait(0.05, 0.09)
    mouse.click("left")
    wait(0.05, 0.09)

def is_visible(screen_object: ScreenObject, img: np.ndarray = None) -> bool:
    return detect_screen_object(screen_object, img).valid

def wait_until_visible(screen_object: ScreenObject, timeout: float = 30, suppress_debug: bool = False) -> TemplateMatch:
    if not (match := _wait_until(lambda: detect_screen_object(screen_object), lambda match: match.valid, timeout)[0]).valid:
        if not suppress_debug:
            Logger.debug(f"{screen_object.ref} not found after {timeout} seconds")
    return match

def wait_until_hidden(screen_object: ScreenObject, timeout: float = 3, suppress_debug: bool = False) -> bool:
    if not (hidden := _wait_until(lambda: detect_screen_object(screen_object).valid, lambda res: not res, timeout)[1]):
        if not suppress_debug:
            Logger.debug(f"{screen_object.ref} still found after {timeout} seconds")
    return hidden

def wait_for_update(img: np.ndarray, roi: list[int] = None, timeout: float = 3, suppress_debug: bool = False) -> bool:
    roi = roi if roi is not None else [0, 0, img.shape[0]-1, img.shape[1] -1]
    if not (change := _wait_until(lambda: cut_roi(grab(), roi), lambda res: not image_is_equal(cut_roi(img, roi), res), timeout)[1]):
        if not suppress_debug:
            Logger.debug(f"ROI: '{roi}' unchanged after {timeout} seconds")
    return change

def _wait_until(func: Callable[[], T], is_success: Callable[[T], bool], timeout = None) -> T | None:
    start = time.time()
    while (time.time() - start) < timeout:
        res = func()
        if (success := is_success(res)):
            break
        wait(0.05)
    return res, success

def hover_over_screen_object_match(match : TemplateMatch) -> None:
    mouse.move(*match.center_monitor)
    wait(0.2, 0.4)

def list_visible_objects(img: np.ndarray = None) -> list:
    img = grab() if img is None else img
    visible=[]
    for pair in [a for a in vars(ScreenObjects).items() if not a[0].startswith('__') and a[1] is not None]:
        if is_visible(pair[1], img):
            visible.append(pair[0])
    return visible

def center_mouse(delay_factor: list = None):
    center_m = convert_abs_to_monitor((0, 0))
    if delay_factor:
        mouse.move(*center_m, randomize=20, delay_factor = delay_factor)
    else:
        mouse.move(*center_m, randomize=20, delay_factor = [0.1, 0.2])

@cache
def get_hud_mask() -> np.ndarray:
    mask = cv2.imread(f"assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
    return cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]

def _find_nearest_nonzero(img: np.ndarray, pos: tuple[int, int]) -> tuple[int, int]:
    """
    Finds the nearest nonzero pixel to the target pixel.
    :param img: The image to search in.
    :param pos: The target pixel
    :return: The nearest nonzero pixel
    """

    x, y = pos
    if x < 0:
        x = 0
    elif x >= img.shape[1]:
        x = img.shape[1] - 1
    if y < 0:
        y = 0
    elif y >= img.shape[0]:
        y = img.shape[0] - 1
    if img[y,x]:
        return (x, y)

    nonzero = cv2.findNonZero(img)
    distances = np.sqrt((nonzero[:,:,0] - x) ** 2 + (nonzero[:,:,1] - y) ** 2)
    nearest_index = np.argmin(distances)
    x, y = nonzero[nearest_index, :, :][0]
    return (x, y)

@cache
def get_closest_non_hud_pixel(pos : tuple[int, int], pos_type: str = "abs") -> tuple[int, int]:
    """
    Finds the closest non-hud pixel to the target pixel.
    :param pos: The target pixel
    :return: The closest non-hud pixel
    """
    if pos is None:
        Logger.error(f"get_closest_non_hud_pixel: Received empty position!")
        return (0,0)
    if isinstance(pos[0], float):
        pos = tuple([round(x) for x in pos])
    match pos_type:
        case "abs":
            pos = convert_abs_to_screen(pos)
        case "monitor":
            pos = convert_monitor_to_screen(pos)
        case "screen":
            pass
        case _:
            Logger.error(f"Unknown pos type: {pos_type}")
            return pos
    screen_pos = _find_nearest_nonzero(get_hud_mask(), pos)
    match pos_type:
        case "abs":
            new_pos = convert_screen_to_abs(screen_pos)
        case "monitor":
            new_pos = convert_screen_to_monitor(screen_pos)
        case "screen":
            new_pos = screen_pos
    return new_pos


# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    from screen import start_detecting_window, grab, stop_detecting_window
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    print("Go to D2R window and press f11 to start")
    keyboard.wait("f11")
    from config import Config

    print(wait_for_update(grab(), Config().ui_roi["right_inventory"], timeout=5))
    # while 1:
    #     print(list_visible_objects())
    #     time.sleep(1)
