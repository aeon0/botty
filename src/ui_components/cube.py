#	- cube transmute

from abc import abstractmethod
from typing_extensions import Self
from config import Config
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from transmute.inventory_collection import InventoryCollection, inspect_area
from utils.custom_mouse import mouse
from utils.misc import wait
import keyboard

from ui_components import ScreenObject, Locator

@Locator(ref=["HORADRIC_CUBE"], roi="left_inventory", threshold=0.8)
class CubeInventory(ScreenObject):
    def open(self) -> 'tuple[CubeOpened, TemplateMatch]':
        self.hover_over_self()
        mouse.click("right")
        wait(0.1)
        return CubeOpened.detect(self.screen, self.finder)


@Locator(ref=["CUBE_TRANSMUTE_BTN"], roi="cube_btn_roi", threshold=0.8)
class CubeOpened(ScreenObject):

    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)
        self._inventory = inspect_area(screen=screen, finder=template_finder, total_rows=4, total_columns=3, roi=Config.ui_roi["cube_area_roi"], known_items=[])

    def transmute(self) -> Self:
        self.hover_over_self()
        mouse.click("left")
        return self

    def close(self) -> 'tuple[CubeInventory, TemplateMatch]':
        keyboard.press("esc")

    def is_empty(self) -> bool:
        return self._inventory.count_empty() == 12



if __name__ == "__main__":

    s = Screen()
    t = TemplateFinder(s)
    res, m = CubeInventory.detect(s, t)
    if m.valid:
        cube, m = res.open()
        print(f'Empty: {cube.is_empty()}')

        if m.valid:
            cube.transmute()
            cube.close()
