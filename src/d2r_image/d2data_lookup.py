import os
import re
import sys
from parse import compile as compile_pattern
from d2r_image.data_models import ItemQuality
from d2r_image.d2data_data import ITEM_ARMOR, ITEM_MISC, ITEM_SET_ITEMS, ITEM_TYPES, ITEM_UNIQUE_ITEMS, ITEM_WEAPONS, REF_PATTERNS, MAGIC_PREFIXES, MAGIC_SUFFIXES
import difflib
from utils.misc import lev

item_lookup: dict = {
    "armor": ITEM_ARMOR,
    "weapons": ITEM_WEAPONS,
    "set_items": ITEM_SET_ITEMS,
    "unique_items": ITEM_UNIQUE_ITEMS,
    "misc": ITEM_MISC,
    "types": ITEM_TYPES,
}
item_lookup_by_display_name: dict = {
    "armor": None,
    "weapons": None,
    "set_items": None,
    "unique_items": None,
    "misc": None,
    "types": None,
}
item_lookup_by_quality_and_display_name: dict = {}
bases_by_name: dict = {}
consumables_by_name: dict = {}
gems_by_name: dict = {}
runes_by_name: dict ={}

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

d2data_path = os.path.join(application_path, 'd2data')
magic_regex = re.compile(r"(^[\w+|']+\s).*(\sOF.*)")

def magic_name(name: str):
    best_similarity = 0
    best_match = None
    for base_item_name in bases_by_name:
        similarity = difflib.SequenceMatcher(None, name, base_item_name).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = base_item_name
    return best_match


def load_lookup():
    for key, val in item_lookup.items():
        # file_path = os.path.join(d2data_path, f'item_{key}.json')
        # with open(file_path, "r",encoding = 'utf-8') as f:
        #     data = json.load(f)
        #     print(f"Loaded {len(data)} records from item_{key}.json")
        #     item_lookup[key] = data
        item_lookup_by_display_name[key] = {value:val[value] for value in val.keys()}
    for quality_key in ['set_items', 'unique_items']:
        item_quality = ItemQuality.Set if quality_key == 'set_items' else ItemQuality.Unique
        if item_quality.value not in item_lookup_by_quality_and_display_name:
            item_lookup_by_quality_and_display_name[item_quality.value] = {}
        for quality_item in item_lookup_by_display_name[quality_key]:
            item_lookup_by_quality_and_display_name[item_quality.value][quality_item.upper()] = item_lookup_by_display_name[quality_key][quality_item]
    for quality_key in ['armor', 'weapons']:
        for quality_item in item_lookup_by_display_name[quality_key]:
            bases_by_name[quality_item.upper().replace(' ', '')] = item_lookup_by_display_name[quality_key][quality_item]
    for extra_base in ['amulet', 'ring', 'grandcharm', 'largecharm', 'smallcharm', 'jewel', 'tomeofidentify', 'tomeoftownportal', 'scrollofidentify', 'scrolloftownportal']:
        bases_by_name[extra_base.upper()] = item_lookup_by_display_name['misc'][extra_base]
    for consumable in [
        'key',
        'scrollofidentify', 'scrolloftownportal',
        'arrows', 'bolts',
        'antidotepotion', 'thawingpotion', 'staminapotion',
        #'Fulminatingpotion', 'Explodingpotion', 'Oilpotion', 'stranglinggaspotion', 'Chokinggaspotion', 'rancidgaspotion',
        'minorhealingpotion', 'lighthealingpotion', 'healingpotion', 'greaterhealingpotion', 'superhealingpotion',
        'minormanapotion', 'lightmanapotion', 'manapotion', 'greatermanapotion', 'supermanapotion',
        'rejuvenationpotion', 'fullrejuvenationpotion',
        'gold'
        ]:
        consumables_by_name[consumable.upper().replace(' ', '')] = item_lookup_by_display_name['misc'][consumable]
    for gem in [
        'chippedruby', 'flawedruby', 'ruby', 'flawlessruby', 'perfectruby',
        'chippedsapphire', 'flawedsapphire', 'sapphire', 'flawlesssapphire', 'perfectsapphire',
        'chippedtopaz', 'flawedtopaz', 'topaz', 'flawlesstopaz', 'perfecttopaz',
        'chippedemerald', 'flawedemerald', 'emerald', 'flawlessemerald', 'perfectemerald',
        'chippeddiamond', 'flaweddiamond', 'diamond', 'flawlessdiamond', 'perfectdiamond',
        'chippedamethyst', 'flawedamethyst', 'amethyst', 'flawlessamethyst', 'perfectamethyst',
        'chippedskull', 'flawedskull', 'skull', 'flawlessskull', 'perfectskull'
    ]:
        gems_by_name[gem.upper().replace(' ', '')] = item_lookup_by_display_name['misc'][gem]
    for misc_item in item_lookup_by_display_name['misc']:
        if 'rune' in misc_item:
            runes_by_name[misc_item.upper().replace(' ', '')] = item_lookup_by_display_name['misc'][misc_item]
    pass

def load_parsers():
    for key, value in REF_PATTERNS.items():
        REF_PATTERNS[key] = {
            "compiled_pattern": compile_pattern(key),
            "identifiers": value
        }

def find_set_or_unique_item_by_name(name, quality: ItemQuality, fuzzy = False):
    if quality.value == ItemQuality.Unique.value:
        return find_unique_item_by_name(name, fuzzy)
    elif quality.value == ItemQuality.Set.value:
        return find_set_item_by_name(name, fuzzy)
    return None

def find_unique_item_by_name(name, fuzzy=False):
    quality = ItemQuality.Unique.value
    normalized_name = normalize_name(name)
    if not fuzzy:
        if normalized_name in item_lookup_by_quality_and_display_name[quality]:
            return item_lookup_by_quality_and_display_name[quality][normalized_name]
    else:
        for item_key in item_lookup_by_quality_and_display_name[quality]:
            if lev(normalized_name, item_key) < 3:
                return item_lookup_by_quality_and_display_name[quality][item_key]

def find_set_item_by_name(name, fuzzy=False):
    # Print where this function gets called from.
    quality = ItemQuality.Set.value
    normalized_name = normalize_name(name)
    if not fuzzy:
        if normalized_name in item_lookup_by_quality_and_display_name[quality]:
            return item_lookup_by_quality_and_display_name[quality][normalized_name]
    else:
        for item_key in item_lookup_by_quality_and_display_name[quality]:
            if lev(normalized_name, item_key) < 3:
                return item_lookup_by_quality_and_display_name[quality][item_key]

def find_base_item_from_magic_item_text(magic_item_text, item_is_identified):
    """
        Unidentified Military Pick is not getting found by this function
    """
    name_to_normalize = magic_item_text
    if item_is_identified:
        name_to_normalize = magic_name(magic_item_text)

    normalized_name = normalize_name(name_to_normalize)
    if normalized_name in bases_by_name:
        return bases_by_name[normalized_name]

    matches = []
    for base_item_name in bases_by_name:
        if base_item_name in normalized_name:
            matches.append(base_item_name)
    return None

def magic_item_is_identified(magic_item_name):
    for affix in MAGIC_PREFIXES:
        if affix in magic_item_name:
            return True
    for affix in MAGIC_SUFFIXES:
        if affix in magic_item_name:
            return True
    return False

def is_base(name: str) -> bool:
    return normalize_name(name) in bases_by_name

def get_base(name):
    if normalize_name(name) in bases_by_name:
        return bases_by_name[normalize_name(name)]
    return None

def is_consumable(name: str):
    return normalize_name(name) in consumables_by_name

def get_consumable(name: str):
    if normalize_name(name) in consumables_by_name:
        return consumables_by_name[normalize_name(name)]
    return None

def is_gem(name: str):
    return normalize_name(name) in gems_by_name

def get_gem(name: str):
    if normalize_name(name) in gems_by_name:
        return gems_by_name[normalize_name(name)]
    return None

def is_rune(name: str):
    return normalize_name(name) in runes_by_name

def get_rune(name: str):
    if normalize_name(name) in runes_by_name:
        return runes_by_name[normalize_name(name)]
    return None

def get_by_name(name: str, _call_count=1):
    """
        Returns the item with the given name, if the item is not found, then recall the function with the hopefully corrected name.
    """
    normalized_name = normalize_name(name)
    if is_base(normalized_name):
        return get_base(normalized_name)
    elif is_consumable(normalized_name):
        return get_consumable(normalized_name)
    elif is_gem(normalized_name):
        return get_gem(normalized_name)
    elif is_rune(normalized_name):
        return get_rune(normalized_name)
    else:
        if _call_count == 2:
            raise Exception("Could not find item with name: " + name)
        return get_by_name(correct_name(name), _call_count=2)

def find_pattern_match(text):
    match = None
    for _, pattern in REF_PATTERNS.items():
        result = pattern["compiled_pattern"].parse(text)
        if result:
            # If the captured data points is an array of one thing, flatten in.
            data_points = result.fixed
            if type(data_points) == tuple and len(data_points) == 1:
                data_points = data_points[0]
            match = {
                "property_id": pattern["identifiers"][0],
                "property_values": data_points
            }
            break
    return match

def find_modifier_pattern_match(modifier_line):
    match = None
    for _, pattern in REF_PATTERNS.items():
        result = pattern["compiled_pattern"].parse(modifier_line)
        if result:
            data_points = result.fixed
            if type(data_points) == tuple and len(data_points) == 1:
                data_points = data_points[0]
            match = {
                "property_id": pattern["identifiers"][0],
                "property_values": data_points
            }
            break
    return match


def normalize_name(name: str):
    return name.replace(' ', '').replace('\'', '').replace('-', '').upper()



def correct_name(name: str):
    items = bases_by_name | consumables_by_name | gems_by_name | runes_by_name
    best_match = None
    best_lev = 0
    for item in items:
        lev_num = lev(name, item)
        if lev_num < 3:
            if best_match is None or lev_num < best_lev:
                best_match = item
                best_lev = lev_num
    if best_match is not None:
        return best_match
    return name


load_lookup()
load_parsers()