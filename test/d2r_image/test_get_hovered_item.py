import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem


@pytest.mark.parametrize("filename, expected_file", [
    ('cold_facet_die.png', 'cold_facet_die.json'),
    ('fire_facet_die.png', 'fire_facet_die.json'),
    ('psn_facet_lvlup.png', 'psn_facet_lvlup.json'),
    ('rare_orb_sell_larzuk.png', 'rare_orb_sell_larzuk.json'),
    ('rare_ring.png', 'rare_ring.json'),
    ('spirit.png', 'spirit.json'),
    ('torch.png', 'torch.json'),
    ('unid_rare_dagger.png', 'unid_rare_dagger.json'),
    ('war_travs.png', 'war_travs.json'),
    ('zod.png', 'zod.json'),
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
