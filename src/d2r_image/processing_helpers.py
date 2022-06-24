import cv2
import numpy as np
import re
import time
import math
import copy

from d2r_image.data_models import GroundItem, GroundItemList, ItemQuality, ItemQualityKeyword, ItemText
from d2r_image.bnip_data import NTIP_ALIAS_QUALITY_MAP
from d2r_image.bnip_helpers import basename_to_types
from d2r_image.ocr import image_to_text
from d2r_image.processing_data import Runeword
import d2r_image.d2data_lookup as d2data_lookup
from d2r_image.d2data_lookup import fuzzy_base_item_match
from d2r_image.processing_data import EXPECTED_HEIGHT_RANGE, EXPECTED_WIDTH_RANGE, GAUS_FILTER, ITEM_COLORS, QUALITY_COLOR_MAP, Runeword, BOX_EXPECTED_HEIGHT_RANGE, BOX_EXPECTED_WIDTH_RANGE
from d2r_image.strings_store import base_items
from utils.misc import color_filter, erode_to_black, slugify
from d2r_image.ocr import image_to_text
from ui_manager import get_hud_mask

from screen import convert_screen_to_monitor
from utils.misc import color_filter, cut_roi, roi_center
from logger import Logger
from config import Config
import template_finder

gold_regex = re.compile(r'(^[0-9]+)\sGOLD')

import time
def crop_text_clusters(inp_img: np.ndarray, padding_y: int = 5) -> list[ItemText]:
    cleaned_img = clean_img(inp_img)
    # Cluster item names
    item_clusters = []
    for key in ITEM_COLORS:
        _, filtered_img = color_filter(cleaned_img, Config().colors[key])
        filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        gaus = GAUS_FILTER
        if key == "gray":
            # white text has some gray on border of glyphs, erode
            filtered_img_gray = cv2.erode(filtered_img_gray, np.ones((2, 1), 'uint8'), None, iterations=1)
            gaus = (GAUS_FILTER[0] + 4, GAUS_FILTER[1])
        blured_img = np.clip(cv2.GaussianBlur(
            filtered_img_gray, gaus, cv2.BORDER_DEFAULT), 0, 255)
        contours = cv2.findContours(
            blured_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            expected_height = EXPECTED_HEIGHT_RANGE[0] < h < EXPECTED_HEIGHT_RANGE[1]
            expected_width = EXPECTED_WIDTH_RANGE[0] < w < EXPECTED_WIDTH_RANGE[1]
            if not (expected_height and expected_width): continue
            # increase height a bit to make sure we have the full item name in the cluster
            y = y - padding_y if y > padding_y else 0
            h += padding_y * 2
            cropped_item = filtered_img[y:y+h, x:x+w]
            avg = int(np.average(filtered_img_gray[y:y+h, x:x+w]))
            contains_black = np.min(cropped_item) < 14
            mostly_dark = avg < 35
            if contains_black and mostly_dark:
                # double-check item color
                color_averages = []
                for key2 in ITEM_COLORS:
                    _, extracted_img = color_filter(cropped_item, Config().colors[key2])
                    extr_avg = np.average(cv2.cvtColor(
                        extracted_img, cv2.COLOR_BGR2GRAY))
                    color_averages.append(extr_avg)
                max_idx = color_averages.index(max(color_averages))
                if key == ITEM_COLORS[max_idx]:
                    item_clusters.append(ItemText(
                        color=key,
                        quality=QUALITY_COLOR_MAP[key],
                        roi=[x, y, w, h],
                        img=inp_img[y:y+h, x:x+w],
                        clean_img=cleaned_img[y:y+h, x:x+w]
                    ))
    cluster_images = [key["clean_img"] for key in item_clusters]
    results = image_to_text(cluster_images, model="ground-eng_inconsolata_inv_th_fast", psm=7, erode=True)
    for count, cluster in enumerate(item_clusters):
        setattr(cluster, "ocr_result", results[count])
    return item_clusters

def crop_item_tooltip(image: np.ndarray, model: str = "hover-eng_inconsolata_inv_th_fast") -> tuple[ItemText, str]:
    """
    Crops visible item description boxes / tooltips
    :inp_img: image from hover over item of interest.
    :model: which ocr model to use
    """
    res = ItemText()
    quality = None
    black_mask = color_filter(image, Config().colors["black"])[0]
    contours = cv2.findContours(
        black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        cropped_item = image[y:y+h, x:x+w]

        if not (expected_height := BOX_EXPECTED_HEIGHT_RANGE[0] < h < BOX_EXPECTED_HEIGHT_RANGE[1]):
            continue
        if not (expected_width := BOX_EXPECTED_WIDTH_RANGE[0] < w < BOX_EXPECTED_WIDTH_RANGE[1]):
            continue

        avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
        if not (mostly_dark := 0 < avg < 35):
            continue
        if not (contains_black := np.min(cropped_item) < 14):
            continue

        contains_white = np.max(cropped_item) > 250
        contains_orange = False
        if not contains_white:
            # check for orange (like key of destruction, etc.)
            orange_mask, _ = color_filter(cropped_item, Config().colors["orange"])
            contains_orange = np.min(orange_mask) > 0
        if not (contains_white or contains_orange):
            continue

        # check to see if contour overlaps right inventory
        right_inv = Config().ui_roi["right_inventory"]
        overlaps_inventory = not (
            x+w < right_inv[0] or right_inv[0]+right_inv[2] < x or y+h+60 < right_inv[1] or right_inv[1]+right_inv[3] < y)
        if not overlaps_inventory:
            left_inv = Config().ui_roi["left_inventory"]
            overlaps_inventory |= not (
                x+w < left_inv[0] or left_inv[0]+left_inv[2] < x or y+h+60 < left_inv[1] or left_inv[1]+left_inv[3] < y)
        if not overlaps_inventory:
            continue

        #print(f"x: {x}, y: {y}, w: {w}, h: {h}")
        footer_y = (y + h) if (y + h) < 700 else 700
        footer_h = 720 - footer_y
        found_footer = template_finder.search(["TO_TOOLTIP"], image, threshold=0.8, roi=[x, footer_y, w, footer_h]).valid
        if found_footer:
            res.ocr_result = image_to_text(cropped_item, psm=6, model=model)[0]
            first_row = cut_roi(copy.deepcopy(cropped_item), (0, 0, w, 26))
            if _contains_color(first_row, "green"):
                quality = ItemQuality.Set.value
            elif _contains_color(first_row, "gold"):
                quality = ItemQuality.Unique.value
            elif _contains_color(first_row, "yellow"):
                quality = ItemQuality.Rare.value
            elif _contains_color(first_row, "blue"):
                quality = ItemQuality.Magic.value
            elif _contains_color(first_row, "orange"):
                quality = ItemQuality.Crafted.value
            elif _contains_color(first_row, "white"):
                quality = ItemQuality.Normal.value
            elif _contains_color(first_row, "gray"):
                if "SUPERIOR" in res.ocr_result.text[:10]:
                    quality = ItemQuality.Superior.value
                else:
                    quality = ItemQuality.Gray.value
            else:
                quality = ItemQuality.Normal.value
            res.roi = [x, y, w, h]
            res.img = cropped_item
            break
    return res, quality

def _contains_color(img: np.ndarray, color: str) -> bool:
    mask = color_filter(img, Config().colors[color])[0]
    return np.average(mask) > 0


def clean_img(inp_img: np.ndarray, black_thresh: int = 14) -> np.ndarray:
    img = inp_img[:, :, :]
    if img.shape[0] == get_hud_mask().shape[0] and img.shape[1] == get_hud_mask().shape[1]:
        img = cv2.bitwise_and(img, img, mask=get_hud_mask())
    # In order to not filter out highlighted items, change their color to black
    highlight_mask = color_filter(img, Config().colors["item_highlight"])[0]
    img[highlight_mask > 0] = (0, 0, 0)
    img = erode_to_black(img, black_thresh)
    return img


def get_items_by_quality(crop_result: list[ItemText]):
    items_by_quality = {}
    for quality in ItemQuality:
        items_by_quality[quality.value] = []
    for item in crop_result:
        quality = None
        if item.quality.value == ItemQuality.Orange.value:
            is_rune = ' RUNE' in item.ocr_result.text
            if is_rune:
                quality = ItemQuality.Rune
            else:
                quality = ItemQuality.Crafted
        elif item.quality.value == ItemQuality.Unique.value:
            is_runeword = False
            try:
                Runeword(item.ocr_result.text)
                is_runeword = True
            except:
                pass
            quality = ItemQuality.Runeword if is_runeword else item.quality
        elif item.quality.value == ItemQuality.Gray.value:
            quality = ItemQuality.Gray
        else:
            quality = item.quality
        items_by_quality[quality.value].append({
            'color': item.color,
            'quality': quality,
            'x': item.roi[0],
            'y': item.roi[1],
            'w': item.roi[2],
            'h': item.roi[3],
            'text': item.ocr_result.text
        })
    return items_by_quality


def consolidate_clusters(items_by_quality):
    if len(items_by_quality) == 0:
        return
    cco_start = time.time()
    consolidate_overlapping_names(items_by_quality)
    cco_end = time.time()
    cco = round(cco_end-cco_start, 2)
    ccr_start = time.time()
    consolidate_rares(items_by_quality)
    ccr_end = time.time()
    ccr = round(ccr_end-ccr_start, 2)
    ccs_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Set.value],
        items_by_quality[ItemQuality.Set.value])
    ccs_end = time.time()
    ccs = round(ccs_end-ccs_start, 2)
    ccu_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Unique.value],
        items_by_quality[ItemQuality.Unique.value])
    ccu_end = time.time()
    ccu = round(ccu_end-ccu_start, 2)
    ccrw_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Runeword.value],
        items_by_quality[ItemQuality.Gray.value])
    ccrw_end = time.time()
    ccrw = round(ccrw_end-ccrw_start, 2)
    # print(f'CCO: {cco}\tCCR: {ccr}\tCCS: {ccs}\tCCU: {ccu}\tCCRW: {ccrw}')


def consolidate_overlapping_names(items_by_quality):
    items_to_remove = {}
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            overlapping_item = None
            for item_to_check in items_by_quality[quality]:
                if item == item_to_check or abs(item['y'] - item_to_check['y']) > 3:
                    continue
                if quality in items_to_remove:
                    if item in items_to_remove[quality] or item_to_check in items_to_remove[quality]:
                        continue
                if item['x'] < item_to_check['x'] + item_to_check['w'] and\
                    item['x'] + item['w'] > item_to_check['x'] and\
                        item['y'] < item_to_check['y'] + item_to_check['h'] and\
                            item['y'] + item['h'] > item_to_check['y']:
                            overlapping_item = item_to_check
                            break
            if overlapping_item:
                first_item = item if item['x'] < overlapping_item['x'] else overlapping_item
                second_item = item if first_item == overlapping_item else overlapping_item
                first_item_text = first_item['text'].strip().replace('\'', '')
                second_item_text = second_item['text'].strip().replace('\'', '').lstrip()
                new_text = f"{first_item_text}\' {second_item_text}"
                if quality == ItemQuality.Set.value:
                    if not d2data_lookup.find_set_item_by_name(new_text):
                        break
                elif quality == ItemQuality.Unique.value:
                    if not d2data_lookup.find_unique_item_by_name(new_text):
                        break
                first_item['text'] = new_text
                first_item['name'] = new_text
                first_item['x'] = first_item['x'] if second_item['x'] > first_item['x'] else second_item['x']
                first_item['y'] = first_item['y'] if second_item['y'] > first_item['y'] else second_item['y']
                first_item['w'] = second_item['x'] + second_item['w'] - first_item['x']
                first_item['h'] = first_item['h']
                if quality not in items_to_remove:
                    items_to_remove[quality] = []
                items_to_remove[quality].append(second_item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            items_by_quality[quality].remove(item)


def consolidate_rares(items_by_quality):
    for item in items_by_quality[ItemQuality.Rare.value]:
        closest_dist = 99999
        closest_base = None
        d2data_base = None
        if not d2data_lookup.is_base(item['text']):
            for base in items_by_quality[ItemQuality.Rare.value]:
                if d2data_lookup.is_base(base['text']):
                    base_item = d2data_lookup.get_base(base['text'])
                    dist = round(math.dist(
                        (item['x'], item['y']),
                        (base['x'], base['y'])
                        ), 0)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_base = base
                        d2data_base = base_item
            if not closest_base:
                return
            item['x'] = item['x'] if closest_base['x'] > item['x'] else closest_base['x']
            item['y'] = item['y'] if closest_base['y'] > item['y'] else closest_base['y']
            item['w'] = item['w'] if closest_base['w'] < item['w'] else closest_base['w']
            item['h'] = item['h'] + closest_base['h']
            item['base'] = d2data_base
            item['item'] = d2data_base
            item['identified'] = True
            items_by_quality[ItemQuality.Rare.value].remove(closest_base)


def consolidate_quality(quality_items, potential_bases):
    bases_to_remove = []
    for item in quality_items:
        if not d2data_lookup.is_base(item['text']):
            # result = d2data_lookup.find_item_by_display_name(item['text'])
            result = d2data_lookup.find_set_or_unique_item_by_name(item['text'], item['quality'])
            if not result:
                continue
            closest_dist = 99999
            closest_base = None
            for base in potential_bases:
                if base['y'] > item['y'] and d2data_lookup.is_base(base['text']):
                    dist = round(math.dist(
                        (item['x'], item['y']),
                        (base['x'], base['y'])
                        ), 0)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_base = base
            if not closest_base:
                continue
            item['x'] = item['x'] if closest_base['x'] > item['x'] else closest_base['x']
            item['y'] = item['y'] if closest_base['y'] > item['y'] else closest_base['y']
            item['w'] = item['w'] if closest_base['w'] < item['w'] else closest_base['w']
            item['h'] = item['h'] + closest_base['h']
            item['item'] = result
            item['name'] = result['DisplayName']
            item['base'] = d2data_lookup.get_base(closest_base['text'])
            item['identified'] = True
            bases_to_remove.append(closest_base)
    for base_to_remove in bases_to_remove:
        potential_bases.remove(base_to_remove)


def find_base_and_remove_items_without_a_base(items_by_quality) -> dict:
    items_to_remove = {}
    gray_normal_magic_removed = {}
    items_to_add = {}
    resolved_runewords = []
    for quality in items_by_quality:
        if quality in [ItemQuality.Gray.value, ItemQuality.Normal.value, ItemQuality.Magic]:
            gray_normal_magic_removed.update(set_gray_and_normal_and_magic_base_items(items_by_quality))
        for item in items_by_quality[quality]:
            quality_keyword, normalized_text = get_normalized_normal_gray_item_text(item['text'])
            if not normalized_text in base_items() and not any(chr.isdigit() for chr in item['text']) and not gold_regex.search(item['text']):
                item['text'] = f"{quality_keyword} {fuzzy_base_item_match(normalized_text)}".strip()
            if 'base' not in item:
                if quality == ItemQuality.Magic.value:
                    base = d2data_lookup.get_base(item['text'])
                    if base:
                        item['base'] = base
                elif quality == ItemQuality.Rune.value:
                    if d2data_lookup.is_rune(item['text']):
                        item['base'] = d2data_lookup.get_rune(item['text'])
                        item['item'] = d2data_lookup.get_rune(item['text'])
                        item['identified'] = True
                elif d2data_lookup.is_base(item['text']):
                    item['base'] = d2data_lookup.get_base(item['text'])
                    item['name'] = item['base']['DisplayName']
                else:
                    if quality not in items_to_remove:
                        items_to_remove[quality] = []
                    items_to_remove[quality].append(item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            if quality == ItemQuality.Unique.value:
                for unique_item in items_by_quality[quality]:
                    if 'item' not in unique_item and 'base' in unique_item and 'uniques' in unique_item['base']:
                        closest_dist = 99999
                        closest_base = None
                        closest_unique_name = None
                        for possible_unique in unique_item['base']['uniques']:
                            normalized_name = possible_unique.replace('_', ' ').upper()
                            if normalized_name in item['text']:
                                dist = round(math.dist(
                                    (item['x'], item['y']),
                                    (unique_item['x'], unique_item['y'])
                                    ), 0)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_base = unique_item
                                    closest_unique_name = normalized_name
                        if  closest_base:
                            unique_name_width = len(closest_unique_name) * 11
                            offset = item['text'].find(closest_unique_name) * 11
                            unique_item['x'] = item['x'] + offset
                            unique_item['y'] -= item['h']
                            unique_item['w'] = unique_name_width if unique_name_width > item['w'] else item['w'] if item['w'] < unique_name_width * 1.4 else unique_name_width
                            unique_item['h'] += item['h']
                            unique_item['text'] = closest_unique_name
                            unique_item['item'] = d2data_lookup.find_unique_item_by_name(closest_unique_name)
                            unique_item['identified'] = True
            elif quality == ItemQuality.Runeword.value:
                if 'item' not in item:
                    closest_dist = 99999
                    closest_base = None
                    for possible_base in items_by_quality[ItemQuality.Gray.value]:
                        dist = round(math.dist(
                            (item['x'], item['y']),
                            (possible_base['x'], possible_base['y'])
                            ), 0)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_base = possible_base
                    if closest_base:
                        closest_base['quality'] = ItemQuality.Runeword
                        closest_base['name'] = item['text']
                        closest_base['x'] = item['x'] if item['x'] < closest_base['x'] else closest_base['x']
                        closest_base['y'] = item['y']
                        closest_base['w'] = item['w'] if item['w'] > closest_base['w'] else closest_base['w']
                        closest_base['h'] += item['h']
                        closest_base['item'] = {}
                        closest_base['identified'] = True
                        if quality not in items_to_add:
                            items_to_add[quality] = []
                        items_to_add[quality].append(closest_base)
                        items_by_quality[ItemQuality.Gray.value].remove(closest_base)
                        resolved_runewords.append(item)
            items_by_quality[quality].remove(item)
    for quality in items_to_add:
        if quality not in items_by_quality:
            items_by_quality[quality] = []
        for item in items_to_add[quality]:
            items_by_quality[quality].append(item)
    for runeword in resolved_runewords:
        if runeword in items_to_remove[ItemQuality.Runeword.value]:
            items_to_remove[ItemQuality.Runeword.value].remove(runeword)
    for quality in gray_normal_magic_removed:
        for item in gray_normal_magic_removed[quality]:
            if item['quality'].value not in items_to_remove:
                items_to_remove[item['quality'].value] = []
            items_to_remove[item['quality'].value].append(item)
    # items_removed = items_to_remove.update(gray_normal_magic_removed)
    return items_to_remove


def get_normalized_normal_gray_item_text(item_text):
    found_keyword_text = None
    if item_text.startswith('OW QUALITY'):
        item_text = item_text.replace('OW QUALITY', ItemQualityKeyword.LowQuality.value)
    if ItemQualityKeyword.LowQuality.value in item_text:
        found_keyword_text = ItemQualityKeyword.LowQuality.value
    elif ItemQualityKeyword.Cracked.value in item_text:
        found_keyword_text = ItemQualityKeyword.Cracked.value
    elif ItemQualityKeyword.Crude.value in item_text:
        found_keyword_text = ItemQualityKeyword.Crude.value
    elif ItemQualityKeyword.Damaged.value in item_text:
        found_keyword_text = ItemQualityKeyword.Damaged.value
    elif ItemQualityKeyword.Superior.value in item_text:
        found_keyword_text = ItemQualityKeyword.Superior.value
    if found_keyword_text:
        return ItemQualityKeyword(found_keyword_text), item_text.replace(f'{found_keyword_text} ', '')
    return None, item_text


def set_gray_and_normal_and_magic_base_items(items_by_quality):
    items_to_remove = {
    }
    for quality in items_by_quality:
        if quality in [ItemQuality.Gray.value, ItemQuality.Normal.value]:
            for item in items_by_quality[quality]:
                quality_keyword, normalized_text = get_normalized_normal_gray_item_text(item['text'])
                result = d2data_lookup.get_base(normalized_text)
                #print(f"{quality_keyword} {normalized_text} {result}")
                if not result:
                    gold_match = gold_regex.search(item['text'])
                    if gold_match:
                        item['base'] = d2data_lookup.get_consumable('GOLD')
                        item['amount'] = gold_match.group(1)
                        continue
                    else:
                        # fuzzy match
                        new_string = ""
                        if quality_keyword:
                            new_string += f"{quality_keyword} "
                        new_string += f"{fuzzy_base_item_match(normalized_text)}"
                        item['text'] = new_string.strip()
                        quality_keyword, normalized_text = get_normalized_normal_gray_item_text(item['text'])
                        result = d2data_lookup.get_base(normalized_text)
                if result:
                    item['base'] = result
                    item['item'] = result
                    item['identified'] = True
                    item['name'] = item['base']['DisplayName']
                    if quality_keyword:
                        item['quality'] = quality_keyword
                else:
                    if d2data_lookup.is_consumable(item['text']):
                        item['base'] = d2data_lookup.get_consumable(item['text'])
                        item['name'] = item['base']['DisplayName']
                    elif d2data_lookup.is_gem(item['text']):
                        item['base'] = d2data_lookup.get_gem(item['text'])
                        item['name'] = item['base']['DisplayName']
                    else:
                        if quality not in items_to_remove:
                            items_to_remove[quality] = []
                        items_to_remove[quality].append(item)
                        # print(f'remove {item}')
        elif quality == ItemQuality.Magic.value:
            for item in items_by_quality[quality]:
                item_is_identified = d2data_lookup.magic_item_is_identified(item['text'])
                base = d2data_lookup.find_base_item_from_magic_item_text(item['text'], item_is_identified)
                if base:
                    item['base'] = base
                    if len(item['text'].lower().replace(base['DisplayName'].lower(), '').replace(' ', '')) > 0:
                        item['item'] = base
                        item['identified'] = True
                    else:
                        item['name'] = base['DisplayName']
                else:
                    if quality not in items_to_remove:
                        items_to_remove[quality] = []
                    items_to_remove[quality].append(item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            items_by_quality[quality].remove(item)
    return items_to_remove


def set_set_and_unique_base_items(items_by_quality):
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            if 'item' in item:
                continue
            item['identified'] = False
            if quality == ItemQuality.Unique.value and 'uniques' in item['base']:
                if len(item['base']['uniques']) == 1:
                    unique_name = item['base']['uniques'][0].replace('_', ' ').upper()
                    item['item'] = d2data_lookup.find_unique_item_by_name(unique_name, True)
                    item['name'] = item['item']['DisplayName']
                else:
                    item['uniqueItems'] = []
                    for unique_item in item['base']['uniques']:
                        unique_name = unique_item.replace('_', ' ').upper()
                        item['uniqueItems'].append(d2data_lookup.find_unique_item_by_name(unique_name, True))
            elif quality == ItemQuality.Set.value and 'sets' in item['base']:
                if len(item['base']['sets']) == 1:
                    set_name = item['base']['sets'][0]
                    item['item'] = d2data_lookup.find_set_item_by_name(set_name, ItemQuality.Set)
                    item['name'] = item['item']['DisplayName']
                else:
                    item['setItems'] = []
                    for unique_item in item['base']['sets']:
                        unique_name = unique_item.replace('_', ' ').upper()
                        item['setItems'].append(d2data_lookup.find_set_item_by_name(unique_name, True))


def build_d2_items(items_by_quality: dict) -> GroundItemList | None:

    ground_item_list = GroundItemList([])
    d2_items = ground_item_list.items
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            try:
                bounding_box = [item['x'], item['y'], item['w'], item['h']]
                bounding_box_monitor = [round(x) for x in [*convert_screen_to_monitor((item['x'], item['y'])), item['w'], item['h']]]
                center = roi_center(bounding_box)
                center_monitor = (round(x) for x in convert_screen_to_monitor(center))
                new_item = GroundItem(
                    BoundingBox=dict(zip(["x", "y", "w", "h"], bounding_box)),
                    BoundingBoxMonitor=dict(zip(["x", "y", "w", "h"], bounding_box_monitor)),
                    Center=dict(zip(["x", "y"], center)),
                    CenterMonitor=dict(zip(["x", "y"], center_monitor)),
                    Distance=round(math.dist((item['x'], item['y']), (Config().ui_pos["screen_width"] / 2, Config().ui_pos["screen_height"] / 2))),
                    Name=item['name'] if 'name' in item else item['text'],
                    Color=item['color'],
                    Quality=item['quality'].value,
                    Text=item['text'],
                    Amount=None if not "amount" in item else item['amount'],
                    BaseItem=item['base'],
                    Item=item['item'] if 'item' in item and item['item'] != item['base'] else None,
                    NTIPAliasType=basename_to_types(item['base']['DisplayName']),
                    # NTIPAliasType=None if item['base']['DisplayName'] not in BNIP_ITEM_TYPE_DATA else BNIP_ITEM_TYPE_DATA[item['base']['DisplayName']],
                    NTIPAliasClassID=item['base']['NTIPAliasClassID'],
                    NTIPAliasClass=item['base']['NTIPAliasClass'] if 'NTIPAliasClass' in item['base'] else None,
                    NTIPAliasQuality=NTIP_ALIAS_QUALITY_MAP[item['quality'].value],
                    NTIPAliasFlag={
                        '0x10': item['identified'],
                        '0x4000000': item['quality'] == ItemQuality.Runeword.value,
                        "0x400000": item['quality'] == ItemQuality.Gray.value,
                    }
                )
                new_item.ID = slugify(f"{new_item.Name}_{'_'.join([str(value) for _, value in new_item.as_dict().items()])}")
                new_item.UID = f"{new_item.ID}_{'_'.join([str(value) for value in center])}"
                if d2_items is None:
                    d2_items = []
                d2_items.append(new_item)
            except Exception as e:
                Logger.error(f'failed on item: {item} with error {e}')
    return ground_item_list

if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, grab, stop_detecting_window
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    print("Go to D2R window and press f11 to start")
    keyboard.wait("f11")
    from config import Config

    # while 1:
    #     img_o = grab()
    #     img = img_o[:, :, :]
    #     # In order to not filter out highlighted items, change their color to black
    #     highlight_mask = color_filter(img, Config().colors["item_highlight"])[0]
    #     img[highlight_mask > 0] = (0, 0, 0)
    #     img = erode_to_black(img, 14)
    #     _, filtered_img = color_filter(img, Config().colors["gray"])
    #     filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
    #     eroded_img_gray = cv2.erode(filtered_img_gray, np.ones((2, 1), 'uint8'), None, iterations=1)
    #     blured_img = np.clip(cv2.GaussianBlur(eroded_img_gray, (17, 1), cv2.BORDER_DEFAULT), 0, 255)
    #     cv2.imshow('test', blured_img)
    #     key = cv2.waitKey(3000)

    while 1:
        img_o = grab()
        tooltip = crop_item_tooltip(img_o)
        print(tooltip)
        cv2.imshow('test', tooltip[0].img)
        #cv2.imshow('test', tooltip[0].ocr_result.processed_img)
        key = cv2.waitKey(20000)