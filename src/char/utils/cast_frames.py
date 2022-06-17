import math
from functools import cache

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
    return get_casting_frames(class_base, skill_name, fcr) * (1/25)