from target_detect import mob_check
import cv2
import pytest

@pytest.mark.parametrize("screen_path", (
    "test/assets/mobs.png",
))
def test_mob_detect(screen_path):
    img = cv2.imread(screen_path)
    assert mob_check(img)

@pytest.mark.parametrize("screen_path", (
    "test/assets/mobs_no_green_or_blue.png",
))
def test_no_mobs(screen_path):
    img = cv2.imread(screen_path)
    assert mob_check(img) == 0
