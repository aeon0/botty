import os
import sys
from parse import compile as compile_pattern
from d2r_image.data_models import ItemQuality
from d2r_image.d2data_data import ITEM_ARMOR, ITEM_MISC, ITEM_SET_ITEMS, ITEM_TYPES, ITEM_UNIQUE_ITEMS, ITEM_WEAPONS, REF_PATTERNS
from d2r_image.strings_store import base_items
from utils.misc import find_best_match
from logger import Logger

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

def magic_name(name: str):
    magic_names = [base_item_name for base_item_name in bases_by_name if base_item_name in name]
    return find_best_match(name, magic_names).match

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
    for extra_base in [
        'amulet',
        'ring',
        'grandcharm',
        'largecharm',
        'smallcharm',
        'jewel',
        'tomeofidentify',
        'tomeoftownportal',
        'keyofterror',
        'keyofhate',
        'keyofdestruction',
        'twistedessenceofsuffering',
        'burningessenceofterror',
        'chargedessenceofhatred',
        'festeringessenceofdestruction'
        ]:
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
        best_match = find_best_match(normalized_name, item_lookup_by_quality_and_display_name[quality].keys()).match
        return item_lookup_by_quality_and_display_name[quality][best_match]

def find_set_item_by_name(name, fuzzy=False):
    quality = ItemQuality.Set.value
    normalized_name = normalize_name(name)
    if not fuzzy:
        if normalized_name in item_lookup_by_quality_and_display_name[quality]:
            return item_lookup_by_quality_and_display_name[quality][normalized_name]
    else:
        best_match = find_best_match(normalized_name, item_lookup_by_quality_and_display_name[quality].keys()).match
        return item_lookup_by_quality_and_display_name[quality][best_match]

def fuzzy_base_item_match(item_name: str, normalized_threshold: float = 0.7):
    if not item_name in base_items():
        fuzzy_res = find_best_match(item_name, list(base_items()))
        if fuzzy_res.match != item_name:
            if fuzzy_res.score_normalized > normalized_threshold and fuzzy_res.match in base_items():
                Logger.debug(f"fuzzy_base_item_match: change {item_name} -> {fuzzy_res.match} (similarity: {fuzzy_res.score_normalized*100:.1f}%)")
                return fuzzy_res.match
            else:
                # Logger.debug(f"fuzzy_base_item_match: proposed {item_name} -> {fuzzy_res.match} (similarity: {fuzzy_res.score_normalized*100:.1f}%) doesn't meet threshold of {normalized_threshold*100:.1f}% or doesn't exist in base items, ignore.")
                pass
    return item_name

def find_base_item_from_magic_item_text(magic_item_text, item_is_identified):
    base_item_str = None
    magic_item_text = magic_item_text.strip()
    if item_is_identified:
        # strip suffix
        of_index = magic_item_text.find(" OF ")
        if of_index > 0:
            words = magic_item_text[:of_index].split()
        else:
            words = magic_item_text.split()
        # iterate through item name by sequentially stripping first word and checking for existence in item bases
        for i in range(len(words)):
            temp_name = ' '.join(words[i:]).strip()
            if temp_name in base_items():
                base_item_str = temp_name
                break
        # failed to find, now try with string correction
        if not base_item_str:
            for i in range(len(words)):
                temp_name = ' '.join(words[i:]).strip()
                if (res := fuzzy_base_item_match(temp_name)) != temp_name:
                    base_item_str = res
                    break
    else:
        if magic_item_text in base_items():
            base_item_str = magic_item_text
        elif (res := fuzzy_base_item_match(magic_item_text)) != magic_item_text:
            base_item_str = res

    if not base_item_str:
        Logger.warning(f"Could not find base item for {magic_item_text}, {item_is_identified}")
        return None
    return get_base(base_item_str)


def magic_item_is_identified(magic_item_name):
    magic_item_name = magic_item_name.upper().replace("-", "").replace("'", "").replace(" ", "")
    for base_by_name in bases_by_name:
        if magic_item_name.upper() == base_by_name:
            return False
    return True

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
    return find_best_match(name, items).match


load_lookup()
load_parsers()