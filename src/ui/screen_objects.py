from dataclasses import dataclass
import numpy as np

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