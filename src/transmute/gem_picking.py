from collections import defaultdict
import itertools
from .stash import Stash

class SimpleGemPicking:

    def __init__(self, s: Stash) -> None:
        self._stash = s
        self._tracking = defaultdict(lambda: list(
            itertools.repeat(0, s.tab_count())))

        for tab in range(self._stash.tab_count()):
            for item in self._stash.get_by_tab(tab).all_items():
                self._tracking[item][tab] += self._stash.get_by_tab(
                    tab).count_by(item)

    def _item_score(self, item) -> float:
        return sum(map(lambda x: x[1] / (x[0]+1.0), enumerate(self._tracking[item])))

    def next_batch(self) -> 'list[(int, str, int, int)]':
        eligible_items = list(filter(
            lambda item: sum(self._tracking[item]) >= 3, self._tracking.keys()
        ))
        best_items = sorted(
            eligible_items, key=lambda item: self._item_score(item), reverse=True
        )
        result = []
        for item in best_items:
            for tab in range(0, self._stash.tab_count()):
                for _ in range(self._stash.get_by_tab(tab).count_by(item)):
                    result.append(
                        (tab, item, *self._stash.pop(tab, item)))
                    self._tracking[item][tab] -= 1

                    if len(result) == 3:
                        return result
        return None
