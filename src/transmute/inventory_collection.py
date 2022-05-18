from collections import defaultdict
from functools import reduce
import itertools
from pipes import Template
from typing_extensions import Self

from config import Config
from screen import grab
import cv2
import numpy as np
import template_finder


def _is_slot_empty(img, treshold=16.0):
    slot_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness > treshold


class InventoryCollection:
    def __init__(self) -> None:
        self._empty_cells = set()
        self._all_items = defaultdict(list)

    def __str__(self) -> str:
        return dict(self._all_items).__str__()

    def append(self, item: str, position: "tuple(int, int)"):
        self._empty_cells.discard(position)
        self._all_items[item].append(position)

    def pop(self, item: str) -> "tuple(int, int)":
        poped = self._all_items[item].pop()
        self._empty_cells.add(poped)
        return poped

    def set_empty(self, position: "tuple(int, int)") -> None:
        self._empty_cells.add(position)

    def count_empty(self) -> int:
        return len(self._empty_cells)

    def count_by(self, item: str):
        return len(self._all_items[item])

    def count(self):
        return reduce(lambda x, y: x + self.count_by(y), self._all_items.keys(), 0)

    def all_items(self):
        return filter(lambda key: len(self._all_items[key]) > 0, self._all_items.keys())


def inspect_area(
    total_rows, total_columns, roi, known_items
) -> InventoryCollection:
    result = InventoryCollection()
    x, y, w, h = roi
    img = grab()[y : y + h, x : x + w]
    slot_w = Config.ui_pos["slot_width"]
    slot_h = Config.ui_pos["slot_height"]
    for column, row in itertools.product(range(total_columns), range(total_rows)):
        y_start, y_end = row * slot_h, slot_h * (row + 1)
        x_start, x_end = column * slot_w, slot_w * (column + 1)
        slot_img = img[y_start:y_end, x_start:x_end]
        if not _is_slot_empty(slot_img[+4:-4, +4:-4], treshold=36):
            result.set_empty((column, row))

        if len(known_items) > 0:
            match = template_finder.search(
                known_items, slot_img, threshold=0.91, best_match=True
            )

            if match.valid:
                result.append(match.name, (column, row))

    return result
