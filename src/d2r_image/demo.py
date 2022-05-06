from copy import deepcopy
import time
import cv2
import keyboard
import os
import json
import dataclasses

from utils.misc import cut_roi, slugify

import d2r_image.processing as processing
from d2r_image.processing import get_hovered_item
from d2r_image.processing_helpers import clean_img, crop_text_clusters
from d2r_image.data_models import ItemQuality, ItemQualityKeyword, ItemText

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

debug_line_map = {}
debug_line_map[ItemQualityKeyword.LowQuality.value] = (123, 123, 123)
debug_line_map[ItemQualityKeyword.Cracked.value] = (123, 123, 123)
debug_line_map[ItemQualityKeyword.Crude.value] = (123, 123, 123)
debug_line_map[ItemQualityKeyword.Superior.value] = (208, 208, 208)
debug_line_map[ItemQuality.Gray.value] = (123, 123, 123)
debug_line_map[ItemQuality.Normal.value] = (208, 208, 208)
debug_line_map[ItemQuality.Magic.value] = (178, 95, 95)
debug_line_map[ItemQuality.Rare.value] = (107, 214, 214)
debug_line_map[ItemQuality.Set.value] = (0, 238, 0)
debug_line_map[ItemQuality.Unique.value] = (126, 170, 184)
debug_line_map[ItemQuality.Crafted.value] = (0, 160, 219)
debug_line_map[ItemQuality.Rune.value] = (0, 160, 219)
debug_line_map[ItemQuality.Runeword.value] = (126, 170, 184)

gen_truth = False

def get_ground_loot():
    print('Loading demo ground images. This may take a few seconds...\n')
    all_image_data = []
    all_images = []
    total_elapsed_time = 0
    demo_image_count = 0
    resource_paths = ['get_ground_loot']
    for resource_path in resource_paths:
        base_dir = f'test/d2r_image/resources/{resource_path}'
        for image_name in os.listdir(base_dir):
            if not image_name.lower().endswith('.png'):
                continue
            image_data = cv2.imread(f"{base_dir}/{image_name}")
            image = deepcopy(image_data)
            start = time.time()
            ground_loot_list = processing.get_ground_loot(image_data)
            end = time.time()
            elapsed = round(end-start, 2)
            print(f'Processed {image_name} in {elapsed} seconds')
            total_elapsed_time += elapsed
            if ground_loot_list.items:
                draw_items_on_image_data(ground_loot_list.items, image_data)
                if gen_truth:
                    gen_truth_from_ground_loot(ground_loot_list.items, image)
                filename_base=image_name.lower()[:-4]
                cv2.imwrite(f"info_screenshots/{filename_base}.png", image_data)
                with open(f"info_screenshots/{filename_base}.json", 'w', encoding='utf-8') as f:
                    json.dump(ground_loot_list, f, ensure_ascii=False, sort_keys=False, cls=EnhancedJSONEncoder, indent=2)
            all_image_data.append(image_data)
            all_images.append(image)
            demo_image_count += 1
    # print('\n')
    print(f'Processing all {demo_image_count} image(s) took {round(total_elapsed_time, 2)} ({round(total_elapsed_time / demo_image_count, 2)} avg)')
    for image in all_image_data:
        cv2.imshow('D2R Image Demo', image)
        cv2.waitKey()
    cv2.destroyAllWindows()
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    print('Press f12 to quit')

def get_hovered_items():
    print('Loading demo hover images. This may take a few seconds...\n')
    all_image_data = []
    all_images = []
    total_elapsed_time = 0
    demo_image_count = 0
    resource_paths = ['get_hovered_item']
    for resource_path in resource_paths:
        base_dir = f'test/d2r_image/resources/{resource_path}'
        files = os.listdir(base_dir)
        for cnt, image_name in enumerate(files):
            if not image_name.lower().endswith('.png'):
                continue
            image_data = cv2.imread(f"{base_dir}/{image_name}")
            image = deepcopy(image_data)
            start = time.time()
            item, res = processing.get_hovered_item(image)
            end = time.time()
            elapsed = round(end-start, 2)
            total_elapsed_time += elapsed
            if res.roi is not None:
                x, y, w, h = res.roi
                cv2.rectangle(image_data, (x, y), (x+w, y+h), (0, 255, 0), 1)
                print(f'Processed {image_name} {cnt+1}/{len(files)} in {elapsed} seconds')
                if gen_truth:
                    gen_truth_from_hovered_item(cut_roi(image, res.roi))
            else:
                print(f'Failed: {image_name} {cnt+1}/{len(files)}')
            if item and item.BaseItem:
                filename_base=image_name.lower()[:-4]
                cv2.imwrite(f"info_screenshots/{filename_base}.png", image_data)
                with open(f"info_screenshots/{filename_base}.json", 'w', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False, sort_keys=False, cls=EnhancedJSONEncoder, indent=2)
            all_image_data.append(image_data)
            all_images.append(image)
            demo_image_count += 1
    print(f'Processing all {demo_image_count} image(s) took {round(total_elapsed_time, 2)} ({round(total_elapsed_time / demo_image_count, 2)} avg)')
    for image in all_image_data:
        cv2.imshow('D2R Image Demo', image)
        cv2.waitKey()
    cv2.destroyAllWindows()
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    print('Press f12 to quit')

def draw_items_on_image_data(items, image):
    for item in items:
        x, y, w, h = item.BoundingBox.values()
        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            debug_line_map[item.Quality],
            1
        )

def gen_truth_from_ground_loot(items, image):

    image = clean_img(image)
    for item in items:
        x, y, w, h = item.BoundingBox.values()
        item_drop = cut_roi(image, [x, y, w, h])
        item_drop = clean_img(item_drop)
        item_slug = slugify({f"{item.Name} {item.Quality}"})
        filename = f"loot_screenshots/ocr_{item_slug}"
        with open(f"{filename}.gt.txt", 'w') as f:
            f.write(item.Text.rstrip())
        cv2.imwrite(f"{filename}.png", item_drop)

def gen_truth_from_hovered_item(tooltip_img):
    contours = crop_text_clusters(tooltip_img)
    for contour in contours:
        contour : ItemText
        basename = f"generated/ground-truth/{time.strftime('%Y%m%d_%H%M%S')}"
        cv2.imshow(time.strftime('%Y%m%d_%H%M%S'), contour.img)
        cv2.waitKey(1)
        print(f"new template: {basename} = ")
        print(f"Enter true text:")
        truth = input()
        if truth:
            if truth == "a":
                string_to_write = contour.ocr_result.text
            else:
                string_to_write = truth
            with open(f"{basename}.gt.txt", 'w') as f:
                f.write(string_to_write)
            cv2.imwrite(f"{basename}.png", template_img)
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            print(f"saved {basename}")
        else:
            print(f"skipped {basename}")    