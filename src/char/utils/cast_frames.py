import math

BASE_FRAMES = {
    "amazon": 20,
    "assassin": 17,
    "barbarian": 14,
    "druid": 15,
    "necromancer": 16,
    "paladin": 16,
    "sorceress": 14,
    "lightning_skills": 19,
}

ANIMATION_SPEED = {
    "default": 256,
    "werewolf": 228,
    "werebear": 229,
}

def _get_base_frames(class_base: str, skill_name: str):
    if "lightning" in skill_name:
        class_base = "lightning_skills"
    if class_base not in BASE_FRAMES:
        class_base = "default"
    return BASE_FRAMES[class_base]

def _get_animation_speed(class_base: str):
    return ANIMATION_SPEED[class_base] if class_base in ANIMATION_SPEED else ANIMATION_SPEED["default"]

def _efcr(fcr: int) -> float:
    return math.floor(fcr * 120 / (fcr + 120))

# =(ROUNDUP((256*B12)/ROUNDDOWN((E12*(100+D12)/100), 0), 0))-1
def _casting_frame_default(class_base: str, skill_name: str, fcr: int):
    return math.ceil(256 * _get_base_frames(class_base, skill_name) / math.floor(_get_animation_speed(class_base) * (100 + _efcr(fcr)) / 100)) - 1

def _casting_frame_lightning(class_base: str, skill_name: str, fcr: int):
    return math.ceil(256 * _get_base_frames(class_base, skill_name) / math.floor(256 * (100 + _efcr(fcr)) / 100))

casting_frame_formula = {
    "default": _casting_frame_default,
    "lightning": _casting_frame_lightning,
    "chain_lightning": _casting_frame_lightning,
}

for i in range(0, 201):
    print(f"{i} {_casting_frame_lightning('sorceress', 'lightning', i)}")