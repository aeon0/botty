import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem
from functools import cache

PATH='test/d2r_image/resources/get_hovered_item'

@cache
def load_hovered_items():
    base_files=[]
    for filename in os.listdir(PATH):
        filename = filename.lower()
        if filename.endswith('.png'):
            basename = filename[:-4].upper()
            base_files.append(basename)
    return base_files

def test_hovered_item():
    base_files = load_hovered_items()
    for base_file in base_files:
        #print(f"Reading {base_file}.png")
        image = cv2.imread(f"{PATH}/{base_file}.png")
        result, _ = processing.get_hovered_item(image)
        expected = HoveredItem.from_json(open(f"{PATH}/{base_file}.json").read())
        assert result == expected
