import cv2
import pytest
import screen

import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called
from target_detect import get_visible_targets
import screen

@pytest.mark.parametrize("screen_path, expected_res", [
    ("test/assets/mobs.png", True),
    ("test/assets/mobs_no_green_or_blue.png", False),
])
def test_target_detect(screen_path, expected_res):
    screen.set_window_position(0, 0)
    img = cv2.imread(screen_path)
    assert bool(len(get_visible_targets(img))) == expected_res

@pytest.mark.parametrize("screen_path, expected_res", [
    ("test/assets/monster_info.png", 0)
])
def test_ignore_immunity_text(screen_path, expected_res):
    screen.set_window_position(0, 0)
    img = cv2.imread(screen_path)
    assert len(get_visible_targets(img)) == expected_res

@pytest.mark.parametrize("screen_path, expected_res", [
    ("test/assets/summon_health_bars.png", 1)
])
def test_ignore_health_bar(screen_path, expected_res):
    # the test asset has a single green glob and health bars in view. If the health bar is ignored, the glob will be the only result
    screen.set_window_position(0, 0)
    img = cv2.imread(screen_path)
    assert len(get_visible_targets(img)) == expected_res

if __name__ == "__main__":
    from config import Config
    import template_finder
    screen.set_window_position(0, 0)

    img = cv2.imread("test/assets/summon_health_bars.png")
    res = template_finder.search_all("summon_health_smallest", img, threshold=0.8, roi=Config().ui_roi["summon_health"], color_match=Config().colors["green"])
    #print(get_visible_targets(img))