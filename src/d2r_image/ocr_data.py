import re
from enum import Enum

I_1 = re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9\-+])")
II_U = re.compile(r"(?<=[A-Z])II|II(?=[A-Z])|1?=[a-z]")
ONE_I = re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]")
ONEONE_U = re.compile(r"(?<=[A-Z])11|11(?=[A-Z])|1?=[a-z]")

ERROR_RESOLUTION_MAP = {
    'SHIFLD': 'SHIELD',
    'SPFAR': 'SPEAR',
    'GLOVFS': 'GLOVES',
    'GOLP': 'GOLD',
    'TELEFORT': 'TELEPORT',
    'TROPHV': 'TROPHY',
    'CLAVMORE': 'CLAYMORE',
    'MAKIMUM': 'MAXIMUM',
    'DEKTERITY': 'DEXTERITY',
    'DERTERITY': 'DEXTERITY',
    'QUAHTITY': 'QUANTITY',
    'DEFERSE': 'DEFENSE',
    'ARMGR': 'ARMOR',
    'ARMER': 'ARMOR',
    'COMDAT': 'COMBAT',
    'WEAPORS': 'WEAPONS',
    'AXECLASS': 'AXE CLASS',
    'IOX%': '10%',
    'IO%': '10%',
    'TWYO': 'TWO',
    'ATTRIOUTES': 'ATTRIBUTES',
    'MONARCHI': 'MONARCH',
    '10 RUNE': 'IO RUNE',
    '1O RUNE': 'IO RUNE',
    'I0 RUNE': 'IO RUNE',
    '1IST RUNE': 'IST RUNE',
    'JAR RUNE': 'JAH RUNE',
    'YO': 'TO',
    'QU AB': 'QUHAB',
    'QUAB': 'QUHAB',
    ' :': ':'
}