from enum import Enum
import keyboard
from logger import Logger
import cv2
import time
import numpy as np
from utils.misc import cut_roi, color_filter, wait
from screen import grab
from config import Config
import template_finder
from ui_manager import wait_until_visible, ScreenObjects
from d2r_image import ocr

class SkillName(str, Enum):
    Attack = 'attack',
    TownPortal = 'town_portal',
    Unsummon = 'unsummon',
    Throw = 'throw',
    # Sorceress
    ## Cold
    IceBolt = 'ice_bolt',
    FrozenArmor = 'frozen_armor',
    FrostNova = 'frost_nova',
    IceBlast = 'ice_blast',
    ShiverArmor = 'shiver_armor',
    GlacialSpike = 'glacial_spike',
    Blizzard = 'blizzard',
    ChillingArmor = 'chilling_armor',
    FrozenOrb = 'frozen_orb',
    ## Lightning
    ChargedBolt = 'charged_bolt',
    StaticField = 'static_field',
    Telekinesis = 'telekinesis',
    Nova = 'nova',
    Lightning = 'lightning',
    ChainLightning = 'chain_lightning',
    Teleport = 'teleport',
    ThunderStorm = 'thunder_storm',
    EnergyShield = 'energy_shield',
    ## Fire
    FireBolt = 'fire_bolt',
    Inferno = 'inferno',
    Blaze = 'blaze',
    Fireball = 'fireball',
    FireWall = 'fire_wall',
    Enchant = 'enchant',
    Meteor = 'meteor',
    Hydra = 'hydra'
    # Paladin
    ## Defensive
    Prayer = 'prayer',
    ResistFire = 'resist_fire',
    Defiance = 'defiance',
    ResistCold = 'resist_cold',
    Cleansing = 'cleansing',
    ResistLightning = 'resist_lightning',
    Vigor = 'vigor',
    Meditation = 'meditation',
    Redemption = 'redemption',
    Salvation = 'salvation',
    ## Offensive
    Might = 'might',
    HolyFire = 'holy_fire',
    Thorns = 'thorns',
    BlessedAim = 'blessed_aim',
    Concentration = 'concentration',
    HolyFreeze = 'holy_freeze',
    HolyShock = 'holy_shock',
    Sanctuary = 'sanctuary',
    Fanaticism = 'fanaticism',
    Conviction = 'conviction',
    ## Combat
    Sacrifice = 'sacrifice',
    Smite = 'smite',
    HolyBolt = 'holy_bolt',
    Zeal = 'zeal',
    Charge = 'charge',
    Vengeance = 'vengeance',
    BlessedHammer = 'blessed_hammer',
    Conversion = 'conversion',
    HolyShield = 'holy_shield',
    FistOfTheHeavens = 'fist_of_the_heavens'
    # Barbarian
    ## Warcries
    Howl = 'howl',
    FindPotion = 'find_potion',
    Taunt = 'taunt',
    Shout = 'shout',
    FindItem = 'find_item',
    BattleCry = 'battle_cry',
    BattleOrders = 'battle_orders',
    GrimWard = 'grim_ward',
    WarCry = 'war_cry',
    BattleCommand = 'battle_command',
    ## Combat
    Bash = 'bash',
    Leap = 'leap',
    DoubleSwing = 'double_swing',
    Stun = 'stun',
    DoubleThrow = 'double_throw',
    LeapAttack = 'leap_attack',
    Concentrate = 'concentrate',
    Frenzy = 'frenzy',
    Whirlwind = 'whirlwind',
    Berserk = 'berserk'
    # Necromancer
    ## Summoning
    RaiseSkeleton = 'raise_skeleton',
    ClayGolem = 'clay_golem',
    RaiseSkeletalMage = 'raise_skeletal_mage',
    BloodGolem = 'blood_golem',
    IronGolem = 'iron_golem',
    FireGolem = 'fire_golem',
    Revive = 'revive',
    ## Poison and Bone
    Teeth = 'teeth',
    BoneArmor = 'bone_armor',
    PoisonDagger = 'poison_dagger',
    CorpseExplosion = 'corpse_explosion',
    BoneWall = 'bone_wall',
    PosionExplosion = 'poison_explosion',
    BoneSpear = 'bone_spear',
    BonePrison = 'bone_prison',
    PoisonNova = 'poison_nova',
    BoneSpirit = 'bone_spirit',
    ## Curses
    AmplifyDamage = 'amplify_damage',
    DimVision = 'dim_vision',
    Weaken = 'weaken',
    IronMaiden = 'iron_maiden',
    Terror = 'terror',
    Confuse = 'confuse',
    LifeTap = 'life_tap',
    Attract = 'attract',
    Decrepify = 'decrepify',
    LowerResist = 'lower_resist'
    # Assassin
    ## Martial Arts
    TigerStrike = 'tiger_strike',
    DragonTalon = 'dragon_talon',
    FistsOfFire = 'fists_of_fire',
    DragonClaw = 'dragon_claw',
    CobraStrike = 'cobra_strike',
    ClawsOfThunder = 'claws_of_thunder',
    DragonTail = 'dragon_tail',
    BladesOfIce = 'blades_of_ice',
    DragonFlight = 'dragon_flight',
    PhoenixStrike = 'phoenix_strike',
    ## Shadow Disciplines
    PsychicHammer = 'psychic_hammer',
    BurstOfSpeed = 'burst_of_speed',
    CloakOfShadows = 'cloak_of_shadows',
    Fade = 'fade',
    ShadowWarrior = 'shadow_warrior',
    MindBlast = 'mind_blast',
    Venom = 'venom',
    ShadowMaster = 'shadow_master',
    ## Traps
    FireBlast = 'fire_blast',
    ShockWeb = 'shock_web',
    BladeSentinel = 'blade_sentinel',
    ChargedBoltSentry = 'charged_bolt_sentry',
    WakeOfFire = 'wake_of_fire',
    BladeFury = 'blade_fury',
    LightningSentry = 'lightning_sentry',
    WakeOfInferno = 'wake_of_inferno',
    DeathSentry = 'death_sentry',
    BladeShield = 'blade_shield'
    # Druid
    ## Elemental
    Firestorm = 'firestorm',
    MoltenBoulder = 'molten_boulder',
    ArcticBlast = 'arctic_blast',
    Fissure = 'fissure',
    CycloneArmor = 'cyclone_armor',
    Twister = 'Twister',
    Volcano = 'volcano',
    Tornado = 'torando',
    Armageddon = 'armageddon',
    Hurricane = 'hurricane',
    ## Shape Shifting
    Werewolf = 'werewolf',
    Werebear = 'werebear',
    FeralRage = 'feral_rage',
    Maul = 'maul',
    Rabies = 'rabies',
    FireClaws = 'fire_claws',
    Hunger = 'hunger',
    ShockWave = 'shock_wave',
    Fury = 'fury',
    ## Summoning
    Raven = 'raven',
    PoisonCreeper = 'poison_creeper',
    OakSage = 'oak_sage',
    SummonSpiritWolf = 'summon_spirit_wolf',
    CarrionVine = 'carrion_vine',
    HeartOfWolverine = 'heart_of_wolverine',
    SummonDireWolf = 'summon_dire_wolf',
    SolarCreeper = 'solar_creeper',
    SpiritOfBarbs = 'spirit_of_barbs',
    SummonGrizzly = 'summon_grizzly'


def is_left_skill_selected(template_list: list[str]) -> bool:
    """
    :return: Bool if skill is currently the selected skill on the left skill slot.
    """
    skill_left_ui_roi = Config().ui_roi["skill_left"]
    for template in template_list:
        if template_finder.search(template, grab(), threshold=0.84, roi=skill_left_ui_roi).valid:
            return True
    return False

def has_tps() -> bool:
    """
    :return: Returns True if botty has town portals available. False otherwise
    """
    from utils import hotkeys
    if SkillName.TownPortal in hotkeys.right_skill_key_map:
        keyboard.send(hotkeys.right_skill_map[SkillName.TownPortal])
        if not (tps_remain := wait_until_visible(ScreenObjects.TownPortalSkill, timeout=4).valid):
            Logger.warning("You are out of tps")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./log/screenshots/info/debug_out_of_tps_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        return tps_remain
    else:
        return False

def select_tp(tp_hotkey):
    templates = template_finder.get_cached_templates_in_dir('assets\\templates\\ui\\skills')
    right_skill = get_selected_skill(templates, grab(), Config().ui_roi["skill_right"])
    if tp_hotkey and right_skill != SkillName.Teleport:
        keyboard.send(tp_hotkey)
        wait(0.1, 0.2)
    right_skill = get_selected_skill(templates, grab(), Config().ui_roi["skill_right"])
    return right_skill == SkillName.Teleport

def is_right_skill_active() -> bool:
    """
    :return: Bool if skill is red/available or not. Skill must be selected on right skill slot when calling the function.
    """
    roi = [
        Config().ui_pos["skill_right_x"] - (Config().ui_pos["skill_width"] // 2),
        Config().ui_pos["skill_y"] - (Config().ui_pos["skill_height"] // 2),
        Config().ui_pos["skill_width"],
        Config().ui_pos["skill_height"]
    ]
    img = cut_roi(grab(), roi)
    avg = np.average(img)
    return avg > 75.0

def is_right_skill_selected(template_list: list[str]) -> bool:
    """
    :return: Bool if skill is currently the selected skill on the right skill slot.
    """
    skill_right_ui_roi = Config().ui_roi["skill_right"]
    for template in template_list:
        if template_finder.search(template, grab(), threshold=0.84, roi=skill_right_ui_roi).valid:
            return True
    return False

def get_skill_charges(img: np.ndarray = None):
    if img is None:
        img = grab()
    x, y, w, h = Config().ui_roi["skill_right"]
    x = x - 1
    y = y + round(h/2)
    h = round(h/2 + 5)
    img = cut_roi(img, [x, y, w, h])
    mask, _ = color_filter(img, Config().colors["skill_charges"])
    ocr_result = ocr.image_to_text(
        images = mask,
        model = "hover-eng_inconsolata_inv_th_fast",
        psm = 7,
        word_list = "",
        scale = 1.4,
        crop_pad = False,
        erode = False,
        invert = True,
        threshold = 0,
        digits_only = True,
        fix_regexps = False,
        check_known_errors = False,
        correct_words = False
    )[0]
    try:
        return int(ocr_result.text)
    except:
        return None

def get_selected_skill(template_list: list[template_finder.Template], img: np.ndarray, roi) -> SkillName:
    """
    :return: 
    """
    matches = template_finder.search_all_templates(
            template_list,
            img,
            threshold=0.9,
            roi=roi,
            use_grayscale=True)
    if len(matches) > 0:
        skill = SkillName(matches[0].name.lower())
        if skill:
            return skill
    return None