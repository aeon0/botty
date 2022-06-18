import os
import cv2
import keyboard
import numpy as np
import template_finder
from config import Config
from screen import find_and_set_window_position, grab
from utils.key_decoder import D2RKeymap
from utils.misc import color_filter, cut_roi, wait


def get_selected_skill(template_list: list[template_finder.Template], img: np.ndarray, roi) -> bool:
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
        return matches[0]
    return None

def discover_hotkey_mappings(templates: list[template_finder.Template], keys_to_check: list[str]):
    key_list = []
    for key in keys_to_check:
        key_to_check = key[0] if key[0] else key[1]
        if key_to_check:
            key_list.append(key_to_check)
    found_keys = []
    left_key_template_map = {}
    right_key_template_map = {}
    img = grab()
    starting_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
    starting_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
    find_keymapping(
        templates,
        key_list,
        starting_left_skill,
        starting_right_skill,
        found_keys,
        left_key_template_map,
        right_key_template_map)
    for key in found_keys:
        if key in key_list:
            key_list.remove(key)
    find_keymapping(
        templates,
        key_list,
        starting_left_skill,
        starting_right_skill,
        found_keys,
        left_key_template_map,
        right_key_template_map)
    for key in found_keys:
        if key in key_list:
            key_list.remove(key)
    if Config().char['cta_available'] and Config().char['weapon_switch']:
        keyboard.press_and_release(Config().char['weapon_switch'])
        find_keymapping(
            templates,
            key_list,
            starting_left_skill,
            starting_right_skill,
            found_keys,
            left_key_template_map,
            right_key_template_map)
        keyboard.press_and_release(Config().char['weapon_switch'])
    ending_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
    ending_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
    return left_key_template_map, right_key_template_map, ending_left_skill.name, ending_right_skill.name

def find_keymapping(
    templates,
    key_list,
    starting_left_skill,
    starting_right_skill,
    found_keys,
    left_key_template_map,
    right_key_template_map):
    previous_left_skill = starting_left_skill
    previous_right_skill = starting_right_skill
    for i in range(0, len(key_list)):
        key = key_list[i]
        print(f'pressing {key}')
        keyboard.press_and_release(key)
        wait(0.3)
        img = grab()
        left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
        right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
        if left_skill != previous_left_skill:
            if key not in left_key_template_map:
                left_key_template_map[left_skill.name.lower()] = []
            left_key_template_map[left_skill.name.lower()].append(key)
            previous_left_skill = left_skill
            found_keys.append(key)
        elif right_skill != previous_right_skill:
            if key not in right_key_template_map:
                right_key_template_map[right_skill.name.lower()] = []
            right_key_template_map[right_skill.name.lower()].append(key)
            previous_right_skill = right_skill
            found_keys.append(key)

# saved_games_folder = 'C:\\Users\\Justin\\Saved Games\\Diablo II Resurrected'
# key_name = 'Foh.key'
# d2r_keymap = D2RKeymap(saved_games_folder, key_name)
# find_and_set_window_position()
# keyboard.wait('f11')
# keyboard.add_hotkey('f12', lambda: os._exit(1))
# #
# keys_to_check = [
#     d2r_keymap.Skill1,
#     d2r_keymap.Skill2,
#     d2r_keymap.Skill3,
#     d2r_keymap.Skill4,
#     d2r_keymap.Skill5,
#     d2r_keymap.Skill6,
#     d2r_keymap.Skill7,
#     d2r_keymap.Skill8,
#     d2r_keymap.Skill9,
#     d2r_keymap.Skill10,
#     d2r_keymap.Skill11,
#     d2r_keymap.Skill12,
#     d2r_keymap.Skill13,
#     d2r_keymap.Skill14,
#     d2r_keymap.Skill15,
#     d2r_keymap.Skill16,
# ]
# templates = template_finder.get_cached_templates_in_dir('assets\\templates\\ui\\skills')
# Debug
# while True:
#     img = grab()
#     left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
#     right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
#     print(f'left: {left_skill}\nright: {right_skill}\n')
#     keyboard.wait('f11')
# Algo
# left_key_template_map, right_key_template_map, left_skill, right_skill = discover_hotkey_mappings(templates)
# key_list = []
# for key in keys_to_check:
#     key_to_check = key[0] if key[0] else key[1]
#     if key_to_check:
#         key_list.append(key_to_check)
# found_keys = []
# left_key_template_map = {}
# right_key_template_map = {}
# img = grab()
# starting_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
# starting_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
# find_keymapping(
#     key_list,
#     starting_left_skill,
#     starting_right_skill,
#     found_keys,
#     left_key_template_map,
#     right_key_template_map)
# for key in found_keys:
#     key_list.remove(key)
# find_keymapping(
#     key_list,
#     starting_left_skill,
#     starting_right_skill,
#     found_keys,
#     left_key_template_map,
#     right_key_template_map)
# ending_left_skill = get_selected_skill(templates, img, Config().ui_roi["skill_left"])
# ending_right_skill = get_selected_skill(templates, img, Config().ui_roi["skill_right"])
# print(left_key_template_map)