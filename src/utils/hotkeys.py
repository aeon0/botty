import os
from enum import Enum
from config import Config
from ui.skills import get_selected_skill
from screen import convert_screen_to_monitor, grab
import template_finder
import keyboard
from utils.custom_mouse import mouse
from utils.misc import wait

d2r_keymap = {}
left_key_template_map = {}
right_skill_key_map = {}
left_skill = None
right_skill = None

class HotkeyName(str, Enum):
    CharacterScreen = 'CharacterScreen',
    InventoryScreen = 'InventoryScreen',
    PartyScreen = 'PartyScreen',
    MercenaryScreen = 'MercenaryScreen',
    MessageLog = 'MessageLog',
    QuestLog = 'QuestLog',
    HelpScreen = 'HelpScreen',
    SkillTree = 'SkillTree',
    SkillSpeedBar = 'SkillSpeedBar',
    Skill1 = 'Skill1',
    Skill2 = 'Skill2',
    Skill3 = 'Skill3',
    Skill4 = 'Skill4',
    Skill5 = 'Skill5',
    Skill6 = 'Skill6',
    Skill7 = 'Skill7',
    Skill8 = 'Skill8',
    Skill9 = 'Skill9',
    Skill10 = 'Skill10',
    Skill11 = 'Skill11',
    Skill12 = 'Skill12',
    Skill13 = 'Skill13',
    Skill14 = 'Skill14',
    Skill15 = 'Skill15',
    Skill16 = 'Skill16',
    SelectPreviousSkill = 'SelectPreviousSkill',
    SelectNextSkill = 'SelectNextSkill',
    ShowBelt = 'ShowBelt',
    UseBelt1 = 'UseBelt1',
    UseBelt2 = 'UseBelt2',
    UseBelt3 = 'UseBelt3',
    UseBelt4 = 'UseBelt4',
    SwapWeapons = 'SwapWeapons',
    Chat = 'Chat',
    Run = 'Run',
    ToggleRunWalk = 'ToggleRunWalk',
    StandStill = 'StandStill',
    ForceMove = 'ForceMove',
    ShowItems = 'ShowItems',
    ShowPortraits = 'ShowPortraits',
    Automap = 'Automap',
    CenterAutomap = 'CenterAutomap',
    FadeAutomap = 'FadeAutomap',
    PartyOnAutomap = 'PartyOnAutomap',
    NamesOnAutomap = 'NamesOnAutomap',
    ToggleMiniMap = 'ToggleMiniMap',
    SayHelp = 'SayHelp',
    SayFollowMe = 'SayFollowMe',
    SayThisIsForYou = 'SayThisIsForYou',
    SayThanks = 'SayThanks',
    SaySorry = 'SaySorry',
    SayBye = 'SayBye',
    SayNowYouDie = 'SayNowYouDie',
    SayRetreat = 'SayRetreat',
    ScreenShot = 'ScreenShot',
    ClearScreen = 'ClearScreen',
    ClearMessages = 'ClearMessages',
    Zoom = 'Zoom',
    LegacyToggle = 'LegacyToggle',
    OpenMenu = 'OpenMenu(Esc)',

def discover_hotkey_mappings(saved_games_folder, key_name):
    global d2r_keymap, left_key_template_map, right_skill_key_map, left_skill, right_skill
    templates = template_finder.get_cached_templates_in_dir('assets\\templates\\ui\\skills')
    d2r_keymap = _parse_key_file(saved_games_folder, key_name)
    key_list = []
    for i in range(1, 17):
        hotkey_name = HotkeyName(f'Skill{i}')
        if hotkey_name in d2r_keymap:
            key_list.append(d2r_keymap[hotkey_name])
    found_keys = []
    img = grab()
    starting_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
    starting_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
    _find_keymapping(
        templates,
        key_list,
        starting_left_skill,
        starting_right_skill,
        found_keys,
        left_key_template_map,
        right_skill_key_map)
    for key in found_keys:
        if key in key_list:
            key_list.remove(key)
    _find_keymapping(
        templates,
        key_list,
        starting_left_skill,
        starting_right_skill,
        found_keys,
        left_key_template_map,
        right_skill_key_map)
    for key in found_keys:
        if key in key_list:
            key_list.remove(key)
    if Config().char['cta_available'] and HotkeyName.SwapWeapons in d2r_keymap:
        keyboard.press_and_release(d2r_keymap[HotkeyName.SwapWeapons])
        _find_keymapping(
            templates,
            key_list,
            starting_left_skill,
            starting_right_skill,
            found_keys,
            left_key_template_map,
            right_skill_key_map)
        wait(0.4)
        keyboard.press_and_release(d2r_keymap[HotkeyName.SwapWeapons])
    ending_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
    ending_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
    left_skill = ending_left_skill
    right_skill = ending_right_skill

def _parse_key_file(saved_games_folder, key_name):
    file = open(os.path.join(saved_games_folder, key_name), 'rb')
    key_bytes = []
    while True:
        byte = file.read(1)
        if byte:
            key_bytes.append(byte)
        else:
            break
    offset = 2
    byte_blocks = []
    while offset < len(key_bytes):
        byte_blocks.append(key_bytes[offset:offset+10])
        offset += 10
    bind_id_map = {
        b'\x00': "CharacterScreen",
        b'\x01': "InventoryScreen",
        b'\x02': "PartyScreen",
        b'\x03': "MessageLog",
        b'\x04': "QuestLog",
        b'\x05': "Chat",
        b'\x06': "HelpScreen",
        b'\x07': "Automap",
        b'\x08': "CenterAutomap",
        b'\t': "FadeAutomap",
        b'\n': "PartyOnAutomap",
        b'\x0b': "NamesOnAutomap",
        b'\x0c': "SkillTree",
        b'\r': "SkillSpeedBar",
        b'\x0e': "Skill1",
        b'\x0f': "Skill2",
        b'\x10': "Skill3",
        b'\x11': "Skill4",
        b'\x12': "Skill5",
        b'\x13': "Skill6",
        b'\x14': "Skill7",
        b'\x16': "ShowBelt",
        b'\x17': "UseBelt1",
        b'\x18': "UseBelt2",
        b'\x19': "UseBelt3",
        b'\x1a': "UseBelt4",
        b'\x1b': "SayHelp",
        b'\x1c': "SayFollowMe",
        b'\x1d': "SayThisIsForYou",
        b'\x1e': "SayThanks",
        b'\x1f': "SaySorry",
        b' ': "SayBye",
        b'!': "SayNowYouDie",
        b'"': "Run",
        b'#': "ToggleRunWalk",
        b'$': "StandStill",
        b'%': "ShowItems",
        b'&': "ClearScreen",
        b"'": "SelectPreviousSkill",
        b'(': "SelectNextSkill",
        b')': "ClearMessages",
        b'*': "ScreenShot",
        b'+': "ShowPortraits",
        b',': "SwapWeapons",
        b'-': "ToggleMiniMap",
        b'\x15': "Skill8",
        b'.': "Skill9",
        b'/': "Skill10",
        b'0': "Skill11",
        b'1': "Skill12",
        b'2': "Skill13",
        b'3': "Skill14",
        b'4': "Skill15",
        b'5': "Skill16",
        b'6': "MercenaryScreen",
        b'7': "SayRetreat",
        b'8': "OpenMenu(Esc)",
        b'9': "Zoom",
        b':': "LegacyToggle",
        b';': "ForceMove"
    }
    found_keymaps = {}
    for block in byte_blocks:
        id = block[0]
        if id in bind_id_map:
            hotkey = _determine_hotkey_from_block(block)
            hotkey_name = HotkeyName(bind_id_map[id])
            if hotkey and hotkey_name not in found_keymaps:
                found_keymaps[hotkey_name] = hotkey
    return found_keymaps

def _determine_hotkey_from_block(byte_block):
    key_value = int(byte_block[4].hex(), 16)
    modifier_value = int(byte_block[5].hex(), 16)
    if key_value in [0, 255]:
        return None
    key = chr(key_value)
    key_correction_map = {
        '\r': 'enter',
        '\t': 'tab',
        ' ': 'space',
        '`': 'NumPad0',
        'a': 'NumPad1',
        'b': 'NumPad2',
        'c': 'NumPad3',
        'd': 'NumPad4',
        'e': 'NumPad5',
        'f': 'NumPad6',
        'g': 'NumPad7',
        'h': 'NumPad8',
        'i': 'NumPad9',
        '-': 'Insert',
        ',': 'ScreenShot',
        'p': 'F1',
        'q': 'F2',
        'r': 'F3',
        's': 'F4',
        't': 'F5',
        'u': 'F6',
        'v': 'F7',
        'w': 'F8',
        'x': 'F9',
        'y': 'F10',
        'z': 'F11',
        '{': 'F12',
        '\x01': 'Mouse4',
        '\x02': 'Mouse5',
        '\x03': 'MouseWheelUp',
        '\x04': 'MouseWheelDown',
        '\x10': 'shift',
        '\x11': 'ctrl',
        '\x12': 'alt',
        '\x1b': 'escape',
        'Ý': ']',
        'Û': '[',
    }
    if key in key_correction_map:
        key = key_correction_map[key]
    modifier_map = {
        16: 'shift',
        32: 'ctrl',
        64: 'alt'
    }
    if modifier_value in modifier_map:
        return f'{modifier_map[modifier_value]}+{key}'
    return key

def _find_keymapping(
    templates,
    key_list,
    starting_left_skill,
    starting_right_skill,
    found_keys,
    left_key_template_map,
    right_key_template_map):
    previous_left_skill = starting_left_skill
    previous_right_skill = starting_right_skill
    for i in range(0, len(key_list)):
        key = key_list[i]
        print(f'pressing {key}')
        keyboard.press_and_release(key)
        wait(0.1)
        img = grab()
        left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
        right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
        print(right_skill, previous_right_skill)
        if left_skill != previous_left_skill:
            previous_left_skill = left_skill
            left_key_template_map[left_skill] = key
            found_keys.append(key)
        elif right_skill != previous_right_skill:
            previous_right_skill = right_skill
            right_key_template_map[right_skill] = key
            found_keys.append(key)

def remap_skill_hotkey(skill_asset, hotkey, skill_roi, expanded_skill_roi):
    x, y, w, h = skill_roi
    x, y = convert_screen_to_monitor((x, y))
    mouse.move(x + w/2, y + h / 2)
    mouse.click("left")
    wait(0.3)
    match = template_finder.search(skill_asset, grab(), threshold=0.84, roi=expanded_skill_roi)
    if match.valid:
        mouse.move(*match.center_monitor)
        wait(0.3)
        keyboard.send(hotkey)
        wait(0.3)
        mouse.click("left")
        wait(0.3)