from target_detect import mob_check
import cv2
import pytest

@pytest.mark.parametrize("screen_path, expected_res", [
    ("test/assets/mobs.png", True),
    ("test/assets/mobs_no_green_or_blue.png", False),
])
def test_mob_detect(screen_path, expected_res):
    img = cv2.imread(screen_path)
    assert bool(mob_check(img)) == expected_res
