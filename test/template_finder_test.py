import cv2
import pytest
from template_finder import TemplateFinder
from utils.misc import is_in_roi

@pytest.mark.parametrize("template1_path, template2_path, template3_path, screen_path, expected_roi", [(
    "test/assets/stash_slot_empty.png", # plain stash slot
    "test/assets/stash_slot_slash.png", # stash slot but has a drawn slash
    "test/assets/stash_slot_cross.png", # stash slot but has a drawn X
    "test/assets/stash_slots.png", # image with three normal squares and one square with draw slash (matching empty_slot-mess)
    [38, 0, 38, 38]) # region of slash
])
def test_match_behavior(template1_path, template2_path, template3_path, screen_path, expected_roi):
    image = cv2.imread(screen_path)
    template1 = cv2.imread(template1_path)
    template2 = cv2.imread(template2_path)
    template3 = cv2.imread(template3_path)
    """
    Test first match
    - searches first for cross, which doesn't perfectly match but should reach above threshold
    - if cross matches above threshold as expected, then it won't bother to search for slash, which has a perfect match on the image
    - test passes if the template match score is not perfect
    """
    match = TemplateFinder().search([template3, template2], image, threshold=0.6)
    assert match.score != 1
    """
    Test best match
    - searches first for slash, which perfectly matches on image
    - also searches for cross, which doesn't perfectly match
    - test passes if the center of the template match lies within the expected region of the slash
    """
    match = TemplateFinder().search([template2, template3], image, threshold=0.6, best_match=True)
    assert is_in_roi(expected_roi, match.center)