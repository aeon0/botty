from target_detect import mob_check
import cv2
import pytest

@pytest.mark.parametrize("screen_path", (
    "test/assets/mobs.png",
))
def test_mob_detect(screen_path):
    img = cv2.imread(screen_path)
    assert mob_check(img)
