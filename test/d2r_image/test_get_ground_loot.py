import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.data_models import D2ItemList, GroundItemList


@pytest.mark.parametrize("filename, expected_items_file", [
    ("ground1.png", 'ground1.json'),
    ("ground2.png", 'ground2.json'),
    ("ground3.png", 'ground3.json'),
    ('ground7.png', 'ground7.json'),
    ("ground13.png", 'ground13.json'),
    ("ground14.png", "ground14.json")
])
def test_ground_loot(filename, expected_items_file):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_ground_loot',
        filename)
    image = cv2.imread(image_path)
    expected_items_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_ground_loot',
        expected_items_file)
    d2_items = processing.get_ground_loot(image)
    ground_expected = GroundItemList.from_json(open(expected_items_path).read())
    assert len(d2_items.items) == len(ground_expected.items)
    for item in ground_expected.items:
        assert item in d2_items.items


def generate_ground_loot_json(image_filename):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_ground_loot',
        image_filename)
    image = cv2.imread(image_path)
    d2_items = processing.get_ground_loot(image)
    ground_expected = D2ItemList([])
    for item in d2_items:
        ground_expected.items.append(item)
    ground_expected_json = ground_expected.to_json()
    print(ground_expected_json)


# generate_ground_loot_json('ground7.png')
# test_ground_loot('ground2.png', 'ground2.json')
