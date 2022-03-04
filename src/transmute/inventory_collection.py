from collections import defaultdict
from dataclasses import dataclass, field
from re import L
from typing import ClassVar, Union

from functools import reduce
import itertools

from pyparsing import col

from config import Config
from screen import detect_window_position, find_and_set_window_position, grab
import cv2
import numpy as np
from template_finder import TemplateFinder
from inventory.known_items import ALL_ITEMS


def _is_slot_empty(img, treshold=16.0):
    slot_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness <= treshold


@dataclass
class InventoryItem:
    _ItemCounter: ClassVar[int] = 0
    id: int = field(init=False)
    type: str
    size: "tuple[int, int]"
    # can add more properties later

    def __post_init__(self):
        InventoryItem._ItemCounter += 1
        self.id = InventoryItem._ItemCounter

EMPTY_CELL = -1
UNKNOWN_ITEM = -2

class InventoryCollection:


    # Internal state of this class is represented by a virtual grid rows x columns and items mapped to that grid
    # We track ids of the items against the grid but also keep a reverse index from id to Item and to it's position

    def __init__(self, rows, columns) -> None:
        self._grid = np.ndarray((rows, columns), int)
        self._grid.fill(EMPTY_CELL)
        self._items_by_type = defaultdict(list)
        self._items = dict()
        self._placement = dict()

    def append(self, item: InventoryItem, placement: "tuple[int, int, int, int]"):
        row_min, row_max, col_min, col_max = placement
        self._grid[row_min:row_max, col_min:col_max].fill(item.id)
        self._items_by_type[item.type].append(item)
        self._items[item.id] = item
        self._placement[item.id] = placement

    def mark_unknown(self, row: int, col: int):
        self._grid[row:row+1, col:col+1].fill(UNKNOWN_ITEM)

    def append_one_cell(self, item: InventoryItem, row: int, col: int):
        self.append(item, (row, row + 1, col, col + 1))

    def _remove_from_grid(self, item: InventoryItem) -> "tuple[int, int, int ,int]":
        row_min, row, col_min, col = self._placement.pop(item.id)
        self._grid[row_min:row, col_min:col].fill(EMPTY_CELL)
        return (row_min, row, col_min, col)

    def pop_by_type(self, type: str) -> "tuple[int, int, int ,int]":
        item: InventoryItem = self._items_by_type[type].pop()
        self._items.pop(item.id)
        return self._remove_from_grid(item)

    def pop_item(self, item: InventoryItem):
        self._items_by_type[item.type].remove(item)
        self._items.pop(item.id)
        return self._remove_from_grid(item)
        

    def get_item_at(self, row: int, col: int) -> "Union[None, InventoryItem]":
        item_id = self._grid[row, col]
        if item_id >= 0:
            return self._items[item_id]
        return None

    def get_item_count(self, type=None):
        if type is None:
            return len(self._items)
        return len(self._items_by_type[type])

    def get_empty_count(self) -> int:
        uniques, counts = np.unique(self._grid, return_counts=True)
        for x, c in zip(uniques, counts):
            if x == EMPTY_CELL:
                return c
        return 0

    def get_types(self) -> list[str]:
        return self._items_by_type.keys()

def inspect_area(total_rows: int, total_columns: int, roi: str, known_items: 'list[str]') -> InventoryCollection:
    result = InventoryCollection(total_rows, total_columns)
    x, y, w, h = roi
    img = grab()[y : y + h, x : x + w]
    slot_w = Config().ui_pos["slot_width"]
    slot_h = Config().ui_pos["slot_height"]
    for item_type in known_items:
        item_description = ALL_ITEMS[item_type]
        for column, row in itertools.product(range(total_columns-item_description.width+1), range(total_rows-item_description.height + 1)):
            y_start, y_end = row * slot_h, slot_h * (row + item_description.height)
            x_start, x_end = column * slot_w, slot_w * (column + item_description.width)
            slot_img = img[y_start:y_end, x_start:x_end]
           
            #cv2.imwrite(f"./crap/im_{column}_{row}.png", slot_img)
            if len(known_items) > 0:
                match = TemplateFinder().search(
                    item_description.assets, slot_img, threshold=0.91, best_match=True
                )

                if match.valid:
                    result.append(
                            InventoryItem(
                                type=item_type, 
                                size=(item_description.width, item_description.height)
                            ),
                            (row, row + item_description.height, column, column+item_description.width)
                        )
                # else:
                #     for inner_col, inner_row in itertools.product(range(item_description.width), range(item_description.height)):
                #         cell_img = slot_img[inner_row * slot_h:(inner_row+1)*slot_h, inner_col*slot_w:(inner_col+1)*slot_w]
                #         cv2.imwrite(f"./crap/im_{column+inner_col}_{row+inner_row}_{inner_col}_{inner_row}.png", cell_img)
                #         if (not result.get_item_at(row + inner_row, column + inner_col) is None) and (not _is_slot_empty(cell_img[+4:-4, +4:-4], treshold=36)):
                #             result.mark_unknown(row + inner_row, column + inner_col)

    return result

if __name__ == "__main__":
    find_and_set_window_position()
    i = inspect_area(4, 3, Config().ui_roi["right_inventory"], ["KEY_OF_XXX", "PERFECT_EMERALD"])
    print(dict(i._items_by_type))
    print(i._grid)
    print(i._placement)
    print(i.get_empty_count())
