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
        threshold=0.8,
        use_grayscale=True
    )
    WaypointLabel=ScreenObject(
        ref="LABEL_WAYPOINT",
        roi="left_panel_label",
        threshold=0.8,
        use_grayscale=True
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
        threshold=0.9,
        use_grayscale=True
    )
    PlayBtn=ScreenObject(
        ref=["PLAY_BTN", "PLAY_BTN_GRAY"],
        roi="play_btn",
        best_match=True
    )
    MainMenu=ScreenObject(
        ref=["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK"],
        roi="main_menu_top_left",
        use_grayscale=True
    )
    Loading=ScreenObject(
        ref=["LOADING", "CREATING_GAME"],
        roi="difficulty_select",
        threshold=0.9
    )
    Normal=ScreenObject(
        ref="NORMAL_BTN",
        roi="difficulty_select",
        threshold=0.9,
        use_grayscale=True
    )
    Nightmare=ScreenObject(
        ref="NIGHTMARE_BTN",
        roi="difficulty_select",
        threshold=0.9,
        use_grayscale=True
    )
    Hell=ScreenObject(
        ref="HELL_BTN",
        roi="difficulty_select",
        threshold=0.9,
        use_grayscale=True
    )
    CubeInventory=ScreenObject(
        ref="HORADRIC_CUBE",
        roi="left_inventory",
        threshold=0.8,
        use_grayscale=True
    )
    CubeOpened=ScreenObject(
        ref="CUBE_TRANSMUTE_BTN",
        roi="cube_btn_roi",
        threshold=0.8,
        use_grayscale=True
    )
    OnlineStatus=ScreenObject(
        ref=["CHARACTER_STATE_ONLINE", "CHARACTER_STATE_OFFLINE"],
        roi="character_online_status",
        best_match=True
    )
    SelectedCharacter=ScreenObject(
        ref="CHARACTER_ACTIVE",
        roi="character_select",
        threshold=0.8
    )
    ServerError=ScreenObject(
        ref="SERVER_ISSUES",
        use_grayscale=True
    )
    SaveAndExit=ScreenObject(
        ref=["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"],
        roi="save_and_exit",
        threshold=0.85,
        use_grayscale=True
    )
    NeedRepair=ScreenObject(
        ref="REPAIR_NEEDED",
        roi="repair_needed",
        use_grayscale=True
    )
    ItemPickupText=ScreenObject(
        ref=["ITEM_PICKUP_ENABLED","ITEM_PICKUP_DISABLED"],
        roi="item_pickup_text",
        best_match=True,
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