from parse import compile as compile_pattern
from d2r_image.d2data_lookup import find_base_item_from_magic_item_text, find_pattern_match, find_set_item_by_name, find_unique_item_by_name, get_base, get_rune, is_base, is_rune, is_consumable, get_consumable, get_by_name
from d2r_image.data_models import HoveredItem, ItemQuality
from d2r_image.nip_data import NIP_ALIAS_STAT_PATTERNS, NIP_PATTERNS, NIP_RE_PATTERNS
from d2r_image.processing_data import Runeword
from utils.misc import lev, find_best_match
from d2r_image.d2data_data import ITEM_NAMES

def correct_item_name(name):
    res = find_best_match(name.lower(), list(map(str.lower,ITEM_NAMES)))
    if res.score < 3:
        return res.match
    return name

def parse_item(quality, item, _call_count=1):
    item_is_identified = True
    item_is_ethereal = False
    item_modifiers = {}
    lines = item.split('\n')
    cleaned_lines = []


    for line in lines:
        if line and 'SELL VALUE' not in line and 'COST' not in line:
            cleaned_lines.append(line)
    lines = cleaned_lines
    for line in lines:

        if lev(line, 'UNIDENTIFIED') < 3:
            item_is_identified = False
        if 'ETHEREAL' in line:
            item_is_ethereal = True
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
    print(lines, item_is_identified)
    base_name = lines[1] if item_is_identified and quality not in [ItemQuality.Superior.value, ItemQuality.Gray.value, ItemQuality.Normal.value, ItemQuality.Magic.value, ItemQuality.Crafted.value] else lines[0]
    base_name = base_name.upper().replace(' ', '')
    base_item = None
    if quality == ItemQuality.Magic.value:
        corrected_name = correct_item_name(cleaned_lines[0]).replace(" ", "")
        base_item = find_base_item_from_magic_item_text(corrected_name, item_is_identified)
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
                if not Runeword(lines[0]):
                    raise Exception('0x1 Unable to find item for: ' + lines[0])
                quality = ItemQuality.Runeword.value
                found_item = {
                    'DisplayName': lines[0]
                }
            else:
                raise Exception('0x2 Unable to find item for: ' + lines[0])
        # parsed_item["item_data_matches"] = find_unique_item_by_name(parsed_item["display_name"]) | find_set_item_by_name(parsed_item["display_name"]) | get_base(parsed_item["base_item"])
        # The next few lines help us determine
        ntip_alias_stat = find_nip_pattern_match(lines)
    else:
        if quality == ItemQuality.Set.value and len(base_item['sets']) == 1:
            found_item = find_set_item_by_name(base_item['sets'][0].replace('_', ' ').upper(), True)
        elif quality == ItemQuality.Unique.value and len(base_item['uniques']) == 1:
            found_item = find_unique_item_by_name(base_item['uniques'][0].replace('_', ' ').upper(), True)
    ntip_alias_quality_map = {
        ItemQuality.Rune.value: 10,
        ItemQuality.Runeword.value: 9,
        ItemQuality.Crafted.value: 8,
        ItemQuality.Unique.value: 7,
        ItemQuality.Rare.value: 6,
        ItemQuality.Set.value: 5,
        ItemQuality.Magic.value: 4,
        ItemQuality.Superior.value: 3,
        ItemQuality.Normal.value: 2,
        ItemQuality.Gray.value: 1
        # TODO Add support for lowquality
    }
    print("base_item", base_item)

    # nip_item = Nip(
    #     NTIPAliasType=base_item['NTIPAliasType'],
    #     NTIPAliasClassID = base_item['NTIPAliasClassID'],
    #     NTIPAliasClass = None if 'item_class' not in base_item else 2 if base_item['item_class'] == 'elite' else 1 if base_item['item_class'] == 'exceptional' else 0,
    #     NTIPAliasQuality=ntip_alias_quality_map[quality],
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
        NTIPAliasQuality=ntip_alias_quality_map[quality],
        NTIPAliasStat=ntip_alias_stat,
        NTIPAliasFlag={
            '0x10': item_is_identified,
            '0x400000': item_is_ethereal,
            '0x4000000': quality == ItemQuality.Runeword.value
        }
    )


def find_nip_pattern_match(item_lines):
    nip_alias_stat = {}
    for pattern, keys in NIP_ALIAS_STAT_PATTERNS.items():
        if pattern not in NIP_RE_PATTERNS:
            NIP_PATTERNS[pattern] = compile_pattern(pattern)
        for line in item_lines:
            result = NIP_PATTERNS[pattern].parse(line.replace('%', ''))
            if result:
                # if len(keys) != len(match.groups(1)):
                #     raise Exception('Mismatch between regex groups and configured NIP keys')
                if len(result.fixed) > 1 and len(keys) == 1:
                    response = None
                    if 'CHARGES' in line:
                        response = {
                            'level': result.fixed[0],
                            'skill': result.fixed[1],
                            'current': result.fixed[2],
                            'max': result.fixed[3]
                        }
                    elif 'CHANCE' in line:
                        response = {
                            'chance': result.fixed[0],
                            'level': result.fixed[1],
                            'skill': result.fixed[2]
                        }
                    if response:
                        nip_alias_stat[keys[0]] = response
                        continue
                for i in range(len(keys)):
                    key = keys[i]
                    if isinstance(key, list):
                        for split_key in key:
                            nip_alias_stat[split_key] = result.fixed[i]
                    else:
                        if result.fixed:
                            nip_alias_stat[key] = result.fixed[i]
                        else:
                            nip_alias_stat[key] = True
    for key in nip_alias_stat:
        if "188," in key: # * There is a mod with the tabskill mod (tab skill means a + to skills of one of the chars skill I.E sorc has Fire skills, paladins have Combat skills, and druids have Summoning skills)
            nip_alias_stat['188'] = nip_alias_stat[key]
            break

    return nip_alias_stat
