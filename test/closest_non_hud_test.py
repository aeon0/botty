import pytest
import screen
from ui_manager import get_closest_non_hud_pixel


@pytest.mark.parametrize("pos, pos_type, should_adapt", [
    ((40, 40), "screen", True), # over merc portrait
    ((1241, 19), "screen", True), # over clock
    ((291, 663), "screen", True), # over health globe
    ((650, 300), "screen", False), # mid screen
    ((783, 618), "screen", True), # over active skill bar
    ((1062, 594), "screen", True), # over gargoyle
    ((0, 0), "abs", False), # mid screen
    ((221, 327), "abs", True), # near right skill
])
def test_get_closest_non_hud_pixel(pos, pos_type, should_adapt):
    screen.set_window_position(0, 0)
    new_pos = get_closest_non_hud_pixel(pos, pos_type)
    is_adapted = not (pos == new_pos)
    assert(is_adapted == should_adapt)