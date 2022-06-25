import math
from functools import cache
from config import Config

BASE_FRAMES = {
    "amazon": 20,
    "assassin": 17,
    "barbarian": 14,
    "druid": 15,
    "necromancer": 16,
    "paladin": 16,
    "sorceress": 14,
    "lightning_skills": 19,
    "default": 20
}

ANIMATION_SPEED = {
    "default": 256,
    "werewolf": 228,
    "werebear": 229,
}

AURAS = {
    "blessed_aim",
    "cleansing",
    "concentration",
    "conviction"
    "defiance",
    "fanaticism",
    "holy_fire",
    "holy_freeze",
    "holy_shock",
    "meditation",
    "might",
    "prayer",
    "redemption",
    "resist_cold",
    "resist_fire",
    "resist_lightning",
    "salvation",
    "sanctuary",
    "thorns",
    "vigor"
}

CHANNELED_SKILLS = {
    "armageddon": 0, # 2.4: removed
    "blade_sentinel": 2,
    "blizzard": 1.8,
    "dragon_flight": 1,
    "fire_wall": 1.4,
    "firestorm": 0.6,
    "fissure": 2,
    "fist_of_the_heavens": 1, # 2.4: 1 -> 0.4
    "frozen_orb": 1,
    "hurricane": 0, # 2.4: removed
    "hydra": 0, # 2.4: removed
    "immolation_arrow": 1,
    "meteor": 1.2,
    "molten_boulder": 1, # 2.4: 2 -> 1
    "plague_javelin": 1, # 2.4: 4 -> 1
    "poison_javelin": 0.6,
    "shadow_master": 0.6, # 2.4: 6 -> 0.6
    "shadow_warrior": 0.6, # 2.4: 6 -> 0.6
    "shock_web": 0.6,
    "valkyrie": 0.6, # 2.4: 6 -> 0.6
    "volcano": 4,
    "werebear": 1,
    "werewolf": 1,
}

def _get_base_frames(class_base: str, skill_name: str):
    if "lightning" in skill_name.lower() and class_base == "sorceress":
        class_base = "lightning_skills"
    if class_base not in BASE_FRAMES:
        class_base = "default"
    return BASE_FRAMES[class_base]

def _get_animation_speed(class_base: str):
    return ANIMATION_SPEED[class_base] if class_base in ANIMATION_SPEED else ANIMATION_SPEED["default"]

def _efcr(fcr: int) -> float:
    return math.floor(fcr * 120 / (fcr + 120))

@cache
def get_casting_frames(class_base: str, skill_name: str, fcr: int):
    if "lightning" in skill_name.lower() and class_base == "sorceress":
        return math.ceil(256 * _get_base_frames(class_base, skill_name) / math.floor(256 * (100 + _efcr(fcr)) / 100))
    else:
        return math.ceil(256 * _get_base_frames(class_base, skill_name) / math.floor(_get_animation_speed(class_base) * (100 + _efcr(fcr)) / 100)) - 1

def get_cast_wait_time(class_base: str, skill_name: str, fcr: int):
    if skill_name in CHANNELED_SKILLS:
        return (math.ceil(get_casting_frames(class_base, skill_name, fcr)/2) + Config().char["extra_casting_frames"]) * (1/25)
    return (get_casting_frames(class_base, skill_name, fcr) + Config().char["extra_casting_frames"]) * (1/25)