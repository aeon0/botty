from target_detect import _process_image, _add_markers, _ignore_targets_within_radius, _sort_targets_by_dist
import cv2
import pytest

@pytest.mark.parametrize("screen_path", (
    "test/assets/mobs.png",
))
def test_mob_detect(screen_path):
    img = cv2.imread(screen_path)
    filterimage, threshz = _process_image(img, mask_char=True, mask_hud=True, info_ss=False, erode=0, dilate=2, blur=4, lh=35, ls=0, lv=43, uh=133, us=216, uv=255, bright=255, contrast=139, thresh=10, invert=0) # HSV Filter for BLUE and GREEN (Posison Nova & Holy Freeze)
    pos_markers = []
    filterimage, _, pos_markers = _add_markers(filterimage, threshz, info_ss=False, rect_min_size=100, rect_max_size=200, marker=True) # rather large rectangles
    filtered_targets = _ignore_targets_within_radius(_sort_targets_by_dist(pos_markers), 150)
    assert len(filtered_targets) >= 3