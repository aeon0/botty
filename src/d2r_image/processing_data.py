from enum import Enum
from d2r_image.data_models import ItemQuality
import cv2

HUD_MASK = cv2.imread(f"assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
HUD_MASK = cv2.threshold(HUD_MASK, 1, 255, cv2.THRESH_BINARY)[1]

ITEM_COLORS = ['white', 'gray', 'blue', 'green', 'yellow', 'gold', 'orange']
GAUS_FILTER = (21, 1)
EXPECTED_HEIGHT_RANGE = [round(num) for num in [x / 1.5 for x in [14, 40]]]
EXPECTED_WIDTH_RANGE = [round(num) for num in [x / 1.5 for x in [60, 1280]]]
BOX_EXPECTED_WIDTH_RANGE = [200, 900]
BOX_EXPECTED_HEIGHT_RANGE = [24, 710]

QUALITY_COLOR_MAP = {
    'white': ItemQuality.Normal,
    'gray': ItemQuality.Gray,
    'blue': ItemQuality.Magic,
    'green': ItemQuality.Set,
    'yellow': ItemQuality.Rare,
    'gold': ItemQuality.Unique,
    'orange': ItemQuality.Orange
}

class Runeword(Enum):
    AncientsPledge='ANCIENT\'S PLEDGE'
    Beast='BEAST'
    Black='BLACK'
    Bone='BONE'
    Bramble='BRAMBLE'
    Brand='BRAND'
    BreathOfTheDying = 'BREATH OF THE DYING'
    CallToArms = 'CALL TO ARMS'
    ChainsOfHonor = 'CHAINS OF HONOR'
    Chaos = 'CHAOS'
    CrescentMoon = 'CRESCENT MOON'
    Death = 'DEATH'
    Delirium = 'DELIRIUM'
    Destruction = 'DESTRUCTION'
    Doom = 'DOOM'
    Dragon = 'DRAGON'
    Dream = 'DREAM'
    Duress = 'DURESS'
    Edge = 'EDGE'
    Enigma = 'EGNIMA'
    Enlightenment = 'ENLIGHTENMENT'
    Eternity = 'ETERNITY'
    Exile = 'EXILE'
    Faith = 'FAITH'
    Famine = 'FAMINE'
    FlickeringFlame = 'FLICKERING FLAME'
    Fortitude = 'FORTITUDE'
    Fury = 'FURY'
    Gloom = 'GLOOM'
    Grief = 'GRIEF'
    HandOfJustice = 'HAND OF JUSTICE'
    Harmony = 'HARMONY'
    HeartOfTheOak = 'HEART OF THE OAK'
    HolyThunder = 'HOLY THUNDER'
    Honor = 'HONOR'
    Ice = 'ICE'
    Infinity = 'INFINITY'
    Insight = 'INSIGHT'
    KingsGrace = 'KING\'S GRACE'
    Kingslayer = 'KINGSLAYER'
    LastWish = 'LAST WISH'
    Lawbringer = 'LAWBRINGER'
    Leaf = 'LEAF'
    Lionheart = 'LIONHEART'
    Lore = 'LORE'
    Malice = 'MALICE'
    Melody = 'MELODY'
    Memory = 'MEMORY'
    Mist = 'MIST'
    Myth = 'MYTH'
    Nadir = 'NADIR'
    Oath = 'OATH'
    Obedience = 'OBEDIENCE'
    Obsession = 'OBSESSION'
    Passion = 'PASSION'
    Pattern = 'PATTERN'
    Peace = 'PEACE'
    Phoenix = 'PHOENIX'
    Plague = 'PLAGUE'
    Pride = 'PRIDE'
    Principle = 'PRINCIPLE'
    Prudence = 'PRUDENCE'
    Radiance = 'RADIANCE'
    Rain = 'RAIN'
    Rhyme = 'RHYME'
    Rift = 'RIFT'
    Sanctuary = 'SANCTUARY'
    Silence = 'SILENCE'
    Smoke = 'SMOKE'
    Spirit = 'SPIRIT'
    Splendor = 'SPLENDOR'
    Stealth = 'STEALTH'
    Steel = 'STEEL'
    Stone = 'STONE'
    Strength = 'STRENGTH'
    Treachery = 'TREACHERY'
    UnbendingWill = 'UNBENDING WILL'
    Venom = 'VENOM'
    VoiceOfReason = 'VOICE OF REASON'
    Wealth = 'WEALTH'
    White = 'WHITE'
    Wind = 'WIND'
    Wisdom = 'WISDOM'
    Wrath = 'WRATH'
    Zephyr = 'ZEPHYR'
