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
import numpy as np
import keyboard


@dataclass
class Locator:
    ref: list[str]
    inp_img: np.ndarray = None
    roi: list[float] = None
    time_out: float = 30
    threshold: float = 0.68
    normalize_monitor: bool = False
    best_match: bool = False
    use_grayscale: bool = False

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
        match = template_finder.search(ref = loc.ref, inp_img = screen.grab(), threshold = loc.threshold, roi = Config.ui_roi[loc.roi], best_match = loc.best_match, use_grayscale = loc.use_grayscale, normalize_monitor = loc.normalize_monitor )
        if match.valid:
            return cls(screen, template_finder, match), match
        return None, match

    @classmethod
    def wait_for(cls: Self, screen: Screen, template_finder: TemplateFinder, time_out: int = None) -> tuple[Self, TemplateMatch]:
        loc = cls.locator()
        time_out = time_out if time_out else loc.time_out
        match = template_finder.search(ref = loc.ref, time_out = time_out, threshold = loc.threshold, roi = Config.ui_roi[loc.roi], best_match = loc.best_match, use_grayscale = loc.use_grayscale, normalize_monitor = loc.normalize_monitor )
        if match.valid:
            return cls(screen, template_finder, match), match
        return None, match


    def hover_over_self(self) -> None:
        mouse.move(*self.screen.convert_screen_to_monitor(self.match.center))
        wait(0.2, 0.4)

    def select_self(self) -> None:
        self.hover_over_self()
        mouse.click("left")
        wait(0.2, 0.4)