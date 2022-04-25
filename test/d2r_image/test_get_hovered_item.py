import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem


@pytest.mark.parametrize("filename, inventory_side, expected_file", [
    ('war_travs.png', 'right', 'war_travs.json'),
    ('unid_hsarus_iron_heel.png', 'right', 'unid_hsarus_iron_heel.json'),
    ('unid_rare_dagger.png', 'right', 'unid_rare_dagger.json'),
    ('cold_skiller.png', 'right', 'cold_skiller.json'),
    ('torch.png', 'right', 'torch.json'),
    ('spirit.png', 'right', 'spirit.json'),
    ('zod.png', 'right', 'zod.json'),
    ('rare_ring.png', 'right', 'rare_ring.json'),
    ('rare_orb_sell_larzuk.png', 'right', 'rare_orb_sell_larzuk.json'),
    ('rare_orb_buy_larzuk.png', 'left', 'rare_orb_buy_larzuk.json'),
])
def test_hovered_item(filename: str, inventory_side: str, expected_file: str):
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
    result, _ = processing.get_hovered_item(image, inventory_side)
    expected = HoveredItem.from_json(open(expected_items_path).read())
    assert result == expected
