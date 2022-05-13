from target_detect import mob_check
import cv2
import pytest
import screen

@pytest.mark.parametrize("screen_path, expected_res", [
    ("test/assets/mobs.png", True),
    ("test/assets/mobs_no_green_or_blue.png", False),
])
def test_mob_detect(screen_path, expected_res):
    screen.set_window_position(0, 0)
    img = cv2.imread(screen_path)
    assert bool(mob_check(img)) == expected_res
