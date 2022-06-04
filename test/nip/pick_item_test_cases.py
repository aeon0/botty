NIP_PICK_TESTS = {
    # monarch
    "001": [
        {
            "Text": "SUPERIOR AEGIS",
            "Color": "gray",
            "expressions": [
                (
                    "[type] == shield && [quality] >= normal && [flag] != ethereal # [sockets] >= 4",
                    True
                ),
                (
                    "[type] == shield",
                    True
                ),
                (
                    "[name] == Aegis && [flag] != ethereal",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior && [flag] == ethereal",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior && [flag] == ethereal # [sockets] >= 4",
                    True
                ),
                (
                    "[name] == Aegis && [flag] == ethereal # [sockets] >= 4",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior && [flag] != ethereal # [sockets] == 0",
                    False
                ),
                (
                    "[name] == Aegis && [flag] == ethereal",
                    True
                ),
                (
                    "[name] == Aegis # [sockets] >= 4",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == normal",
                    False
                ),
                (
                    "[quality] == normal",
                    False
                ),
            ],
        },
        {
            "Color": "gray",
            "Text": "AEGIS",
            "expressions": [
                (
                    "[name] == Aegis && [quality] == normal",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior",
                    False
                ),
                (
                    "[name] == Aegis && [flag] == ethereal",
                    True
                ),
                (
                    "[name] == Aegis # [sockets] > 0",
                    True
                ),
            ],
        },
        {
            "Color": "gray",
            "Text": "AERIN SHIELD",
            "expressions": [
                (
                    "[type] == auricshields # [sockets] > 0",
                    True
                ),
                (
                    "[name] == aerinshield # [sockets] > 0",
                    True
                ),
                (
                    "[type] == auricshields && [flag] != ethereal # [sockets] == 0",
                    False
                ),
                (
                    "[type] == auricshields && [flag] != ethereal # [sockets] > 0",
                    True
                ),
                (
                    "[name] == aerinshield && [flag] != ethereal # [sockets] == 0",
                    False
                ),
                (
                    "[name] == aerinshield && [flag] != ethereal # [sockets] > 0",
                    True
                ),
                (
                    "[name] == aerinshield",
                    True
                ),
            ],
        },
        {
            "Color": "gray",
            "Text": "SUPERIOR AERIN SHIELD",
            "expressions": [
                (
                    "[type] == auricshields && [quality] == superior && [flag] != ethereal # [sockets] > 0",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "13935 GOLD",
            "expressions": [
                (
                    "[Type] == Gold # [Gold] >= 1000",
                    True
                ),
                (
                    "[Type] == Gold # [Gold] < 1000",
                    False
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "AEGIS",
            "expressions": [
                (
                    "[name] == Aegis # [sockets] == 0",
                    True
                ),
                (
                    "[name] == Aegis # [sockets] > 0",
                    False
                ),
                (
                    "[name] == Aegis && [quality] == normal",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == superior",
                    False
                ),
                (
                    "[name] == Aegis && [quality] > normal",
                    False
                ),
            ],
        },
        {
            "Color": "blue",
            "Text": "AEGIS",
            "expressions": [
                (
                    "[name] == Aegis && [quality] == magic",
                    True
                ),
                (
                    "[name] == Aegis && [quality] == magic # [sockets] == 0",
                    True
                ),
                (
                    "[name] == Aegis && [quality] >= superior",
                    True
                ),
                (
                    "[name] == Aegis && [quality] <= superior",
                    False
                ),
            ],
        },
        {
            "Color": "yellow",
            "Text": "AEGIS",
            "expressions": [
                (
                    "[name] == Aegis && [quality] == rare",
                    True
                ),
            ],
        },
        {
            "Color": "gold",
            "Text": "AEGIS",
            "expressions": [
                (
                    "[name] == aegis && [quality] == unique",
                    True
                ),
            ],
        },
    ],
    "045": [
        {
            "Color": "gray",
            "Text": "GREATER CLAWS",
            "expressions": [
                (
                    "[name] == greaterclaws && [quality] == normal",
                    True
                ),
                (
                    "[type] == assassinclaw && [quality] == normal",
                    True
                ),
                (
                    "[type] == handtohand && [quality] == normal",
                    True
                ),
            ],
        },
        {
            "Color": "gray",
            "Text": "SUPERIOR GREATER CLAWS",
            "expressions": [
                (
                    "[type] == handtohand && [quality] == superior",
                    True
                ),
                (
                    "[name] == greaterclaws && [quality] == superior",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "GREATER CLAWS",
            "expressions": [
                (
                    "[name] == greaterclaws && [flag] != ethereal && [quality] <= superior # [sockets] == 0 && [skilldragonflight] >= 2 && [skilllightningsentry] >= 2 ",
                    True
                ),
            ],
        },
        {
            "Color": "gold",
            "Text": "GREAT SWORD",
            "expressions": [

            ],
        },
    ],
    "188": [
        {
            "Color": "white",
            "Text": "FLAWED EMERALD",
            "expressions": [
                (
                    "[name] >= chippedemerald && [name] <= perfectemerald",
                    True
                ),
                (
                    "[name] == flawedemerald",
                    True
                ),
                (
                    "[name] == emerald",
                    False
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "FULL REJUVENATION POTION",
            "expressions": [
                (
                    "[name] == fullrejuvenationpotion",
                    True
                ),
                (
                    "[name] == rejuvenationpotion",
                    False
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "FLAWLESS SKULL",
            "expressions": [

            ],
        },
        {
            "Color": "orange",
            "Text": "FESTERING ESSENCE OF DESTRUCTION",
            "expressions": [
                (
                    "[name] == festeringessenceofdestruction",
                    True
                ),
            ],
        },
    ],
    "191": [
        {
            "Color": "white",
            "Text": "REJUVENATION POTION",
            "expressions": [
                (
                    "[name] == fullrejuvenationpotion",
                    False
                ),
                (
                    "[name] == rejuvenationpotion",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "SUPER MANA POTION",
            "expressions": [
                (
                    "[name] == supermanapotion",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "SCROLL OF TOWN PORTAL",
            "expressions": [
                (
                    "[name] == scrolloftownportal",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "SCROLL OF IDENTIFY",
            "expressions": [
                (
                    "[name] == scrollofidentify",
                    True
                ),
            ],
        },
        {
            "Color": "white",
            "Text": "SUPER HEALING POTION",
            "expressions": [
                (
                    "[name] == superhealingpotion",
                    True
                ),
            ],
        },
        {
            "Color": "green",
            "Text": "RING",
            "expressions": [
                (
                    "[name] == ring && [quality] == set",
                    True
                ),
                (
                    "[type] == ring && [quality] == set # [hpregen] >= 2 && [maxhp] >= 15 // Angelic Halo",
                    True
                ),
            ],
        },
        {
            "Color": "orange",
            "Text": "SUR RUNE",
            "expressions": [
                (
                    "[name] >= elrune && [name] <= zodrune",
                    True
                ),
                (
                    "[name] == surrune",
                    True
                ),
            ],
        },
    ],
}