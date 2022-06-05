from config import Config
from dataclasses import dataclass
from logger import Logger
from d2r_image.data_models import HoveredItem

@dataclass
class Consumables:
    tp: int = 0
    id: int = 0
    rejuv: int = 0
    health: int = 0
    mana: int = 0
    key: int = 0
    def __getitem__(self, key):
        return super().__getattribute__(key)
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def any_needs(self):
        return sum([self.tp, self.id, self.rejuv, self.health, self.mana, self.key])
    def as_dict(self):
        return {
            "tp": self.tp,
            "id": self.id,
            "rejuv": self.rejuv,
            "health": self.health,
            "mana": self.mana,
            "key": self.key
        }
consumable_needs = Consumables()

ITEM_CONSUMABLES_MAP = {
    "rejuvenation potion": "rejuv",
    "full rejuvenation potion": "rejuv",
    "rejuvpotion": "rejuv",
    "super healing potion": "health",
    "greater healing potion": "health",
    "healing potion": "health",
    "healingpotion": "health",
    "light healing potion": "health",
    "minor healing potion": "health",
    "super mana potion": "mana",
    "greater mana potion": "mana",
    "mana potion": "mana",
    "manapotion": "mana",
    "light mana potion": "mana",
    "minor mana potion": "mana",
    "scroll of town portal": "tp",
    "scroll of identify": "id",
    "key": "key"
}
pot_cols = {
    "rejuv": Config().char["belt_rejuv_columns"],
    "health": Config().char["belt_hp_columns"],
    "mana": Config().char["belt_mp_columns"],
}

def get_needs(consumable_type: str = None):
    if consumable_type:
        consumable = reduce_name(consumable_type)
        return consumable_needs[consumable]
    return consumable_needs

def set_needs(consumable_type: str, quantity: int):
    global consumable_needs
    consumable = reduce_name(consumable_type)
    consumable_needs[consumable] = quantity

def increment_need(consumable_type: str = None, quantity: int = 1):
    """
    Adjust the consumable_needs of a specific consumable
    :param consumable_type: Name of item in pickit or in consumable_map
    :param quantity: Increase the need (+int) or decrease the need (-int)
    """
    global consumable_needs
    consumable = reduce_name(consumable_type)
    consumable_needs[consumable] = max(0, consumable_needs[reduce_name(consumable)] + quantity)

def reduce_name(consumable_type: str):
    if consumable_type.lower() in ITEM_CONSUMABLES_MAP:
        consumable_type = ITEM_CONSUMABLES_MAP[consumable_type]
    elif consumable_type.lower() in ITEM_CONSUMABLES_MAP.values():
        pass
    else:
        Logger.warning(f"adjust_consumable_need: unknown item: {consumable_type}")
    return consumable_type

def get_remaining(item_name: str = None) -> int:
    if item_name is None:
        Logger.error("get_remaining: param item_name is required")
        return -1
    if item_name.lower() in ["health", "mana", "rejuv"]:
        return pot_cols[item_name] * Config().char["belt_rows"] - consumable_needs[item_name]
    elif item_name.lower() in ['tp', 'id']:
        return 20 - consumable_needs[item_name]
    elif item_name.lower() == "key":
        return 12 - consumable_needs[item_name]
    else:
        Logger.error(f"get_remaining: error with item_name={item_name}")
        return -1

def should_buy(item_name: str = None, min_remaining: int = None, min_needed: int = None) -> bool:
    if item_name is None:
        Logger.error("should_buy: param item_name is required")
        return False
    if min_needed:
        return consumable_needs[item_name] >= min_needed
    elif min_remaining:
        return get_remaining(item_name) <= min_remaining
    else:
        Logger.error("should_buy: need to specify min_remaining or min_needed")
    return False

def is_consumable(item: HoveredItem) -> str | bool:
    for consumable_type in ITEM_CONSUMABLES_MAP.keys():
        if item.Name.lower() == consumable_type:
            return consumable_type
    return False