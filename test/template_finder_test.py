import cv2
import pytest
import template_finder
from utils.misc import is_in_roi
import screen

@pytest.mark.parametrize("template1_path, template2_path, template3_path, screen_path, expected_roi", [(
    "test/assets/stash_slot_empty.png", # empty stash slot
    "test/assets/stash_slot_slash.png", # empty stash slot but has a drawn slash
    "test/assets/stash_slot_cross.png", # empty stash slot but has a drawn X
    "test/assets/stash_slots.png", # image with three empty slots and one slot with a draw slash
    [38, 0, 38, 38]) # region of slash
])
def test_match_behavior(template1_path, template2_path, template3_path, screen_path, expected_roi):
    screen.set_window_position(0, 0)
    image = cv2.imread(screen_path)
    empty = cv2.imread(template1_path)
    slash = cv2.imread(template2_path)
    cross = cv2.imread(template3_path)
    threshold=0.6
    """
    Test first match
    - searches first for cross, which doesn't perfectly match but should reach above threshold
    - if cross matches above threshold as expected, then it won't bother to search for slash, which has a perfect match on the image
    - test passes if the template match score is not perfect
    """
    match = template_finder.search([cross, slash], image, threshold)
    assert threshold <= match.score < 1
    """
    Test best match
    - searches first for cross, which doesn't perfectly match
    - searches next for slash, which perfectly matches on image
    - test passes if the center of the template match lies within the expected region of the slash
    """
    match = template_finder.search([cross, slash], image, threshold=0.6, best_match=True)
    assert is_in_roi(expected_roi, match.center)
    """
    Test all matches
    - searches for empty slots with high threshold
    - test passes if 3 matches result
    """
    matches = template_finder.search_all(empty, image, threshold=0.98)
    assert len(matches) == 3