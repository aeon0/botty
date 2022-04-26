from functools import cache

_word_list_dir = "assets/word_lists"

@cache
def all_words():
    with open(f"{_word_list_dir}/all_words.txt", 'r') as f:
        return f.read().splitlines()

@cache
def base_items():
    with open(f"{_word_list_dir}/base_items.txt", 'r') as f:
        return f.read().splitlines()

@cache
def magic_prefixes():
    with open(f"{_word_list_dir}/magic_prefixes.txt", 'r') as f:
        return f.read().splitlines()

@cache
def magic_suffixes():
    with open(f"{_word_list_dir}/magic_suffixes.txt", 'r') as f:
        return f.read().splitlines()