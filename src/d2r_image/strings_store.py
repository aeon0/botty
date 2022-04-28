from functools import cache

_WORD_LIST_DIR = "assets/word_lists"

@cache
def all_words():
    with open(f"{_WORD_LIST_DIR}/all_words.txt", 'r') as f:
        return set(line.strip() for line in f.read().splitlines())

@cache
def base_items():
    with open(f"{_WORD_LIST_DIR}/base_items.txt", 'r') as f:
        return set(line.strip() for line in f.read().splitlines())

@cache
def magic_prefixes():
    with open(f"{_WORD_LIST_DIR}/magic_prefixes.txt", 'r') as f:
        return set(line.strip() for line in f.read().splitlines())

@cache
def magic_suffixes():
    with open(f"{_WORD_LIST_DIR}/magic_suffixes.txt", 'r') as f:
        return set(line.strip() for line in f.read().splitlines())