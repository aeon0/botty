from dataclasses import dataclass


@dataclass
class ItemDescription:
    width: int
    height: int
    assets: "list[str]"  # need a collection as charms for instance can have different look


ALL_ITEMS: "dict[str, ItemDescription]" = {
    "FLAWLESS_EMERALD": ItemDescription(
        assets=["INVENTORY_EMERALD_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_EMERALD": ItemDescription(
        assets=["INVENTORY_EMERALD_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_SAPPHIRE": ItemDescription(
        assets=["INVENTORY_SAPPHIRE_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_SAPPHIRE": ItemDescription(
        assets=["INVENTORY_SAPPHIRE_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_DIAMOND": ItemDescription(
        assets=["INVENTORY_DIAMOND_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_DIAMOND": ItemDescription(
        assets=["INVENTORY_DIAMOND_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_AMETHYST": ItemDescription(
        assets=["INVENTORY_AMETHYST_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_AMETHYST": ItemDescription(
        assets=["INVENTORY_AMETHYST_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_RUBY": ItemDescription(
        assets=["INVENTORY_RUBY_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_RUBY": ItemDescription(
        assets=["INVENTORY_RUBY_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_SKULL": ItemDescription(
        assets=["INVENTORY_SKULL_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_SKULL": ItemDescription(
        assets=["INVENTORY_SKULL_PERFECT"], width=1, height=1
    ),
    "FLAWLESS_TOPAZ": ItemDescription(
        assets=["INVENTORY_TOPAZ_FLAWLESS"], width=1, height=1
    ),
    "PERFECT_TOPAZ": ItemDescription(
        assets=["INVENTORY_TOPAZ_PERFECT"], width=1, height=1
    ),
    "KEY_OF_XXX": ItemDescription(assets=["INVENTORY_KEY_OF_XXX"], width=1, height=2),
}