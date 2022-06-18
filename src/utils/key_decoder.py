import os


class D2RKeymap:
    CharacterScreen: str = None
    InventoryScreen: str = None
    PartyScreen: str = None
    MessageLog: str = None
    QuestLog: str = None
    Chat: str = None
    Help: str = None
    Automap: str = None
    CenterAutomap: str = None
    FadeAutomap: str = None
    PartyOnAutomap: str = None
    NamesOnAutomap: str = None
    SkillTree: str = None
    SkillSpeedBar: str = None
    Skill1: str = None
    Skill2: str = None
    Skill3: str = None
    Skill4: str = None
    Skill5: str = None
    Skill6: str = None
    Skill7: str = None
    ShowBelt: str = None
    UseBelt1: str = None
    UseBelt2: str = None
    UseBelt3: str = None
    UseBelt4: str = None
    SayHelp: str = None
    SayFollowMe: str = None
    SayThisIsForYou: str = None
    SayThanks: str = None
    SaySorry: str = None
    SayBye: str = None
    SayNowYouDie: str = None
    Run: str = None
    ToggleRunWalk: str = None
    StandStill: str = None
    ShowItems: str = None
    ClearScreen: str = None
    SelectPreviousSkill: str = None
    SelectNextSkill: str = None
    ClearMessages: str = None
    ScreenShot: str = None
    ShowPortraits: str = None
    SwapWeapons: str = None
    ToggleMinimap: str = None
    Skill8: str = None
    Skill9: str = None
    Skill10: str = None
    Skill11: str = None
    Skill12: str = None
    Skill13: str = None
    Skill14: str = None
    Skill15: str = None
    Skill16: str = None
    MercenaryScreen: str = None
    SayRetreat: str = None
    OpenMenu: str = None
    Zoom: str = None
    LegacyToggle: str = None
    ForceMove: str = None

    def __init__(self, saved_games_folder, key_name):
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
                if bind_id_map[id] not in found_keymaps:
                    found_keymaps[bind_id_map[id]] = []
                found_keymaps[bind_id_map[id]].append(
                    self._determine_hotkey_from_block(block))
        for key in found_keymaps:
            self.__dict__[key] = found_keymaps[key]

    def _determine_hotkey_from_block(self, byte_block):
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
