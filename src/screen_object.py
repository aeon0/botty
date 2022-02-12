from abc import abstractmethod
from dataclasses import dataclass
from math import fabs
from typing import Generic, TypeVar
from typing_extensions import Self
from config import Config
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from transmute.inventory_collection import InventoryCollection, inspect_area
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
import keyboard
@dataclass
class Locator:
    assets: list[str]
    roi: str
    treshold: float
    best_match = False

    def __call__(self, cls):
        cls._locator = self
        return cls

class ScreenObject:
    _locator = None

    @classmethod
    def locator(cls) -> Locator:
        return cls._locator

    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        self.match = match
        self.screen = screen
        self.finder = template_finder
    
    @classmethod
    def detect(cls: Self, screen: Screen, template_finder: TemplateFinder) -> tuple[Self, TemplateMatch]:
        loc = cls.locator()
        match = template_finder.search(loc.assets, screen.grab(), loc.treshold, Config.ui_roi[loc.roi], loc.best_match)
        if match.valid:
            return cls(screen, template_finder, match), match
        else:
            Logger.debug(f'not matching: {match}')
        return None, match

    def hover_over_self(self) -> None:
        mouse.move(*self.screen.convert_screen_to_monitor(self.match.center))
        wait(0.1, 0.2)


@Locator(assets=["HORADRIC_CUBE"], roi="left_inventory", treshold=0.8)        
class CubeInventory(ScreenObject):
    def open(self) -> 'tuple[CubeOpened, TemplateMatch]':
        self.hover_over_self()
        mouse.click("right")
        wait(0.1)
        return CubeOpened.detect(self.screen, self.finder)


@Locator(assets=["CUBE_TRANSMUTE_BTN"], roi="cube_btn_roi", treshold=0.8)        
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
    