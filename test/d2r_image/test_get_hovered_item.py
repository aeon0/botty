import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem


@pytest.mark.parametrize("filename, expected_file", [
    ('hovered_item_20220504_160228.png', 'hovered_item_20220504_160228.json'),
    ('hovered_item_20220504_160419.png', 'hovered_item_20220504_160419.json'),
    ('hovered_item_20220504_161007.png', 'hovered_item_20220504_161007.json'),
    ('hovered_item_20220504_161026.png', 'hovered_item_20220504_161026.json'),
    ('hovered_item_20220504_161113.png', 'hovered_item_20220504_161113.json'),
    ('hovered_item_20220504_161131.png', 'hovered_item_20220504_161131.json'),
    ('hovered_item_20220504_161338.png', 'hovered_item_20220504_161338.json'),
])
def test_hovered_item(filename: str, expected_file: str):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_hovered_item',
        f'{filename}')
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    expected_items_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_hovered_item',
        expected_file)
    result, _ = processing.get_hovered_item(image)
    expected = HoveredItem.from_json(open(expected_items_path).read())
    assert result == expected
