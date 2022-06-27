import cv2
import pytest
import template_finder
from utils.misc import is_in_roi
import screen
import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called

screen.set_window_position(0, 0)

def test_search():
    """
    Test default search behavior (first match)
    - searches first for cross, which doesn't perfectly match but should reach above threshold
    - if cross matches above threshold as expected, then it won't bother to search for slash, which has a perfect match on the image
    - test passes if the template match score is not perfect
    """
    image = cv2.imread("test/assets/stash_slots.png")
    slash = cv2.imread("test/assets/stash_slot_slash.png")
    cross = cv2.imread("test/assets/stash_slot_cross.png")
    threshold=0.6
    match = template_finder.search([cross, slash], image, threshold)
    assert threshold <= match.score < 1

def test_search_best_match():
    """
    Test search "best_match" behavior
    - searches first for cross, which doesn't perfectly match
    - searches next for slash, which perfectly matches on image
    - test passes if the center of the template match lies within the expected region of the slash
    """
    image = cv2.imread("test/assets/stash_slots.png")
    slash = cv2.imread("test/assets/stash_slot_slash.png")
    cross = cv2.imread("test/assets/stash_slot_cross.png")
    slash_expected_roi = [38, 0, 38, 38]
    match = template_finder.search([cross, slash], image, threshold=0.6, best_match=True)
    assert is_in_roi(slash_expected_roi, match.center)

def test_search_all():
    """
    Test all matches for a single template in argument
    - searches for empty slots with high threshold
    - test passes if 3 matches result
    """
    image = cv2.imread("test/assets/stash_slots.png")
    empty = cv2.imread("test/assets/stash_slot_empty.png")
    matches = template_finder.search_all(empty, image, threshold=0.98)
    assert len(matches) == 3

def test_search_all_multiple_templates():
    """
    Test all matches with multiple templates in argument
    - searches for empty slots and slash with high threshold
    - test passes if 4 matches result
    """
    image = cv2.imread("test/assets/stash_slots.png")
    empty = cv2.imread("test/assets/stash_slot_empty.png")
    slash = cv2.imread("test/assets/stash_slot_slash.png")
    matches = template_finder.search_all([empty, slash], image, threshold=0.98)
    assert len(matches) == 4

if __name__ == "__main__":
    image = cv2.imread("test/assets/stash_slots.png")
    empty = cv2.imread("test/assets/stash_slot_empty.png")
    slash = cv2.imread("test/assets/stash_slot_slash.png")
    cross = cv2.imread("test/assets/stash_slot_cross.png")
    slash_expected_roi = [38, 0, 38, 38]


    matches = template_finder.search_all([empty, slash], image, threshold=0.98)
    print(len(matches))
    print(matches)
