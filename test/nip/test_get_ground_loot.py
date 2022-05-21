import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.data_models import D2ItemList, GroundItemList
from functools import cache

PATH='test/assets/ground_loot'

@cache
def load_ground_loot():
    base_files=[]
    for filename in os.listdir(PATH):
        filename = filename.lower()
        if filename.endswith('.png'):
            basename = filename[:-4].upper()
            base_files.append(basename)
    return base_files

def test_ground_loot():
    base_files = load_ground_loot()
    for base_file in base_files:
        #print(f"Reading {base_file}.png")
        img = cv2.imread(f"{PATH}/{base_file}.png")
        d2_items = processing.get_ground_loot(img)
        ground_expected = GroundItemList.from_json(open(f"{PATH}/{base_file}.json").read())
        #print(f"  items: {len(d2_items.items)}")
        assert len(d2_items.items) == len(ground_expected.items)
        for item in ground_expected.items:
            assert item in d2_items.items


def generate_ground_loot_json(image_filename):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'assets',
        'ground_loot',
        image_filename)
    image = cv2.imread(image_path)
    d2_items = processing.get_ground_loot(image)
    ground_expected = D2ItemList([])
    for item in d2_items:
        ground_expected.items.append(item)
    ground_expected_json = ground_expected.to_json()
    #print(ground_expected_json)


# generate_ground_loot_json('ground7.png')
# test_ground_loot('ground2.png', 'ground2.json')
