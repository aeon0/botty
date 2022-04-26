from functools import cached_property

class WordLists:
    def __init__(self):
        self._word_list_dir = "assets/word_lists"

    @cached_property
    def all_words(self):
        with open(f"{self._word_list_dir}/all_words.txt", 'r') as f:
            return f.read().splitlines()

    @cached_property
    def base_items(self):
        with open(f"{self._word_list_dir}/base_items.txt", 'r') as f:
            return f.read().splitlines()

    @cached_property
    def magic_prefixes(self):
        with open(f"{self._word_list_dir}/magic_prefixes.txt", 'r') as f:
            return f.read().splitlines()

    @cached_property
    def magic_suffixes(self):
        with open(f"{self._word_list_dir}/magic_suffixes.txt", 'r') as f:
            return f.read().splitlines()