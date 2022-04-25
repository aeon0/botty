from copy import deepcopy
import time
import cv2
import keyboard
import os
import d2r_image.processing as processing
from d2r_image.processing import get_hovered_item
from d2r_image.data_models import ItemQuality, ItemQualityKeyword


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
            # print(f'Processed {image} in {elapsed} seconds')
            total_elapsed_time += elapsed
            if ground_loot_list.items:
                draw_items_on_image_data(ground_loot_list.items, image_data)
                cv2.imwrite(f"info_screenshots/{image_name.lower()}", image_data)
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
    resource_paths = ['get_hovered_item']
    for resource_path in resource_paths:
        base_dir = f'test/d2r_image/resources/{resource_path}'
        for image_name in os.listdir(base_dir):
            if not image_name.lower().endswith('.png'):
                continue
            image_data = cv2.imread(f"{base_dir}/{image_name}")
            item, _ = get_hovered_item(image_data, 'right' if resource_path == 'hover_right' else 'left')
            cv2.imshow('Hovered Item', image_data)
            cv2.waitKey()
    cv2.destroyAllWindows()

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