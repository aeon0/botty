from parse import compile as compile_pattern
from d2r_image.d2data_lookup import find_base_item_from_magic_item_text, find_pattern_match, find_set_item_by_name, find_unique_item_by_name, get_base, get_rune, is_base, is_rune, is_consumable, get_consumable, get_by_name
from d2r_image.data_models import HoveredItem, ItemQuality
from d2r_image.nip_data import NIP_ALIAS_STAT_PATTERNS, NTIP_ALIAS_QUALITY_MAP
from d2r_image.processing_data import Runeword
from rapidfuzz.string_metric import levenshtein
import re
from logger import Logger

from parse import compile
from functools import cache

@cache
def compiled_nip_patterns():
    nip_patterns = {}
    for pattern in NIP_ALIAS_STAT_PATTERNS.keys():
        nip_patterns[pattern] = compile(pattern)
    return nip_patterns

def parse_item(quality, item, _call_count=1):
    item_is_identified = True
    item_is_ethereal = False
    item_modifiers = {}
    lines = item.splitlines()
    cleaned_lines = []


    for line in lines:
        if line and 'SELL VALUE' not in line and 'COST' not in line:
            cleaned_lines.append(line)
    lines = cleaned_lines
    for line in lines:
        if levenshtein(line, 'UNIDENTIFIED') < 3:
            item_is_identified = False
        if 'ETHEREAL' in line:
            item_is_ethereal = True
        if item_is_ethereal and not item_is_identified:
            break
    if item_is_identified:
        for line in lines:
            match = find_pattern_match(line)
            if match:
                # Store the property values
                # if match["property_id"] not in parsed_item:
                #     parsed_item[match["property_id"]] = []
                # parsed_item[match["property_id"]].append(match["property_values"])
                if match["property_id"] not in item_modifiers:
                    item_modifiers[match["property_id"]] = []
                item_modifiers[match["property_id"]].append(match["property_values"])
    # The first line is usually the item name
    # parsed_item["display_name"] = item[0]
    # The second line is usually the type. Map it to be sure, (for now just setting to base_type)
    # parsed_item["base_item"] = item[1]
    # print(lines, item_is_identified)
    base_name = lines[1] if item_is_identified and quality not in [ItemQuality.Superior.value, ItemQuality.Gray.value, ItemQuality.Normal.value, ItemQuality.Magic.value, ItemQuality.Crafted.value] else lines[0]
    base_name = base_name.upper().replace(' ', '')
    base_item = None
    if quality == ItemQuality.Magic.value:
        base_item = find_base_item_from_magic_item_text(cleaned_lines[0], item_is_identified)
    else:
        if quality == ItemQuality.Crafted.value and is_rune(base_name):
            base_item = get_rune(base_name)
            quality = ItemQuality.Rune.value
        else:
            normalized_base_name = base_name[:8] == "SUPERIOR" and base_name[8:] or base_name # * if superior is prefix, remove it
            found_base = get_by_name(normalized_base_name)
            if found_base:
                base_item = found_base
            else:
                raise Exception('Unable to find item base for: ' + base_name)

    # Add matches from item data
    found_item = None
    ntip_alias_stat = None
    if item_is_identified:
        if quality == ItemQuality.Unique.value:
            found_item = find_unique_item_by_name(lines[0].replace(' ', ''))
        elif quality == ItemQuality.Set.value:
            found_item = find_set_item_by_name(lines[0].replace(' ', ''))
        elif quality in [ItemQuality.Superior.value, ItemQuality.Gray.value, ItemQuality.Normal.value, ItemQuality.Rune.value, ItemQuality.Crafted.value]:
            found_item = base_item
        if not found_item and quality not in [ItemQuality.Magic.value, ItemQuality.Rare.value]:
            if quality == ItemQuality.Unique.value:
                if not Runeword(lines[0].replace(' ', '')):
                    raise Exception('0x1 Unable to find item for: ' + lines[0].replace(' ', ''))
                quality = ItemQuality.Runeword.value
                found_item = {
                    'DisplayName': lines[0].replace(' ', '')
                }
            else:
                raise Exception('0x2 Unable to find item for: ' + lines[0].replace(' ', ''))
        # parsed_item["item_data_matches"] = find_unique_item_by_name(parsed_item["display_name"]) | find_set_item_by_name(parsed_item["display_name"]) | get_base(parsed_item["base_item"])
        # The next few lines help us determine
        ntip_alias_stat = find_nip_pattern_match(lines)
    else:
        if quality == ItemQuality.Set.value and len(base_item['sets']) == 1:
            found_item = find_set_item_by_name(base_item['sets'][0].replace('_', ' ').upper(), True)
        elif quality == ItemQuality.Unique.value and len(base_item['uniques']) == 1:
            found_item = find_unique_item_by_name(base_item['uniques'][0].replace('_', ' ').upper(), True)
    # print("base_item", base_item)

    # nip_item = Nip(
    #     NTIPAliasType=base_item['NTIPAliasType'],
    #     NTIPAliasClassID = base_item['NTIPAliasClassID'],
    #     NTIPAliasClass = None if 'item_class' not in base_item else 2 if base_item['item_class'] == 'elite' else 1 if base_item['item_class'] == 'exceptional' else 0,
    #     NTIPAliasQuality=NTIP_ALIAS_QUALITY_MAP[quality],
    #     NTIPAliasStat=ntip_alias_stat,
    #     NTIPAliasFlag={
    #         '0x10': item_is_identified,
    #         '0x4000000': item_is_ethereal
    #     }
    # )
    # d2_data = D2Data(
    #     BaseItem=base_item,
    #     Item=found_item,
    #     ItemModifiers=item_modifiers if item_modifiers else None
    # )
    # return {
    #     'name': lines[0],
    #     'quality': quality,
    #     'text': '|'.join(lines),
    #     'baseItem': base_item,
    #     'item': found_item,
    #     'itemModifiers': ntip_alias_stat
    # }
    # print(found_item, base_item)
    name = (found_item and found_item['DisplayName']) or (base_item and base_item['DisplayName'])
    if quality in [ItemQuality.Magic.value, ItemQuality.Rare.value]:
        if item_is_identified:
            name = lines[0]
        else:
            name = base_item['DisplayName']
    return HoveredItem(
        Name=name,
        NTIPAliasIdName=lines[0].replace(" ", "").replace("\"", "").replace("'", ""),
        Quality=quality,
        Text='|'.join(lines),
        BaseItem=base_item,
        Item=found_item,
        NTIPAliasType=base_item['NTIPAliasType'],
        NTIPAliasClassID=base_item['NTIPAliasClassID'],
        NTIPAliasClass = None if 'item_class' not in base_item else 2 if base_item['item_class'] == 'elite' else 1 if base_item['item_class'] == 'exceptional' else 0,
        NTIPAliasQuality=NTIP_ALIAS_QUALITY_MAP[quality],
        NTIPAliasStat=ntip_alias_stat,
        NTIPAliasFlag={
            '0x10': item_is_identified,
            '0x400000': item_is_ethereal,
            '0x4000000': quality == ItemQuality.Runeword.value
        }
    )

def find_nip_pattern_match(item_lines):
    nip_alias_stat = {}

    for line in item_lines:
        #print(f"  line: {line}")
        for pattern, ntip_alias_keys in NIP_ALIAS_STAT_PATTERNS.items():
            result = compiled_nip_patterns()[pattern].parse(line)
            if result:
                #print(f"    ntip_alias_keys: {ntip_alias_keys}")
                #print(f"    result: {result}")
                for item_prop_cnt, item_prop in enumerate(result.fixed):
                    #print(f"      item_prop: {item_prop}, item_prop_cnt: {item_prop_cnt}")
                    try:
                        if isinstance(ntip_alias_keys[item_prop_cnt], list):
                            for sub_alias_key in ntip_alias_keys[item_prop_cnt]:
                                nip_alias_stat[sub_alias_key] = item_prop
                        else:
                            if result.fixed:
                                nip_alias_stat[ntip_alias_keys[item_prop_cnt]] = item_prop
                            else:
                                nip_alias_stat[ntip_alias_keys[item_prop_cnt]] = True
                    except IndexError:
                        # more item properties than read fields, skip
                        Logger.warning(f"IndexError on line: {line}, ntip_alias_keys: {ntip_alias_keys}, result: {result}, item_prop: {item_prop}, item_prop_cnt: {item_prop_cnt}")
                    except Exception as e:
                        Logger.error(f"error {e}\n  on line: {line}, ntip_alias_keys: {ntip_alias_keys}, result: {result}, item_prop: {item_prop}, item_prop_cnt: {item_prop_cnt}")
                break
    for key in nip_alias_stat.copy(): # it don't like when I change the dict while iterating
        # find stats like 83,3=2 (+2 to paladins skills) and also add 83=2
        found_group = re.search(r'(\d+),', key)
        if found_group:
            nip_alias_stat[found_group.group(1)] = nip_alias_stat[key]
    return nip_alias_stat

def _handle_skill_properties():
    # '195' = itemskillonattack
    # '196' = itemskillonkill
    # '197' = itemskillondeath
    # '198' = itemskillonhit
    # '199' = itemskillonlevelup
    # '201' = itemskillongethit
    # '204 = itemchargedskill


    pass