BNIP_PICK_TESTS = {
    # monarch
    "001": [
        {
            "Text": "SUPERIOR AEGIS",
            "Color": "gray",
            "expressions": [
                {
                    "expression": "[type] == shield && [quality] >= normal && [flag] != ethereal # [sockets] >= 4",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == shield",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [flag] != ethereal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior && [flag] == ethereal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior && [flag] == ethereal # [sockets] >= 4",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [flag] == ethereal # [sockets] >= 4",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior && [flag] != ethereal # [sockets] == 0",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == Aegis && [flag] == ethereal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis # [sockets] >= 4",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == normal",
                    "should_pickup": False
                },
                {
                    "expression": "[quality] == normal",
                    "should_pickup": False
                },
            ],
        },
        {
            "Color": "gray",
            "Text": "AEGIS",
            "expressions": [
                {
                    "expression": "[name] == Aegis && [quality] == normal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == Aegis && [flag] == ethereal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis # [sockets] > 0",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "gray",
            "Text": "AERIN SHIELD",
            "expressions": [
                {
                    "expression": "[type] == auricshields # [sockets] > 0",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == aerinshield # [sockets] > 0",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == auricshields && [flag] != ethereal # [sockets] == 0",
                    "should_pickup": False
                },
                {
                    "expression": "[type] == auricshields && [flag] != ethereal # [sockets] > 0",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == aerinshield && [flag] != ethereal # [sockets] == 0",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == aerinshield && [flag] != ethereal # [sockets] > 0",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == aerinshield",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "gray",
            "Text": "SUPERIOR AERIN SHIELD",
            "expressions": [
                {
                    "expression": "[type] == auricshields && [quality] == superior && [flag] != ethereal # [sockets] > 0",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "13935 GOLD",
            "expressions": [
                {
                    "expression": "[Type] == Gold # [Gold] >= 1000",
                    "should_pickup": True
                },
                {
                    "expression": "[Type] == Gold # [Gold] < 1000",
                    "should_pickup": False
                },
            ],
        },
        {
            "Color": "white",
            "Text": "AEGIS",
            "expressions": [
                {
                    "expression": "[name] == Aegis # [sockets] == 0",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis # [sockets] > 0",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == Aegis && [quality] == normal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == superior",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == Aegis && [quality] > normal",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == Aegis && [class] == elite",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "blue",
            "Text": "AEGIS",
            "expressions": [
                {
                    "expression": "[name] == Aegis && [quality] == magic",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] == magic # [sockets] == 0",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] >= superior",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == Aegis && [quality] <= superior",
                    "should_pickup": False
                },
            ],
        },
        {
            "Color": "yellow",
            "Text": "AEGIS",
            "expressions": [
                {
                    "expression": "[name] == Aegis && [quality] == rare",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "gold",
            "Text": "AEGIS",
            "expressions": [
                {
                    "expression": "[name] == aegis && [quality] == unique",
                    "should_pickup": True
                },
            ],
        },
    ],
    "045": [
        {
            "Color": "gray",
            "Text": "GREATER CLAWS",
            "expressions": [
                {
                    "expression": "[name] == greaterclaws && [quality] == normal",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == greaterclaws && [class] == exceptional",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == assassinclaw && [quality] == normal",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == handtohand && [quality] == normal",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "gray",
            "Text": "SUPERIOR GREATER CLAWS",
            "expressions": [
                {
                    "expression": "[type] == handtohand && [quality] == superior",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == greaterclaws && [quality] == superior",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "GREATER CLAWS",
            "expressions": [
                {
                    "expression": "[name] == greaterclaws && [flag] != ethereal && [quality] <= superior # [sockets] == 0 && [skilldragonflight] >= 2 && [skilllightningsentry] >= 2 ",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "gold",
            "Text": "GREAT SWORD",
            "expressions": [

            ],
        },
    ],
    "139": [
        {
            "Color": "white",
            "Text": "SUPERIOR HIEROPHANT TROPHY",
            "expressions": [
                {
                    "expression": "[name] == hierophanttrophy",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == voodooheads",
                    "should_pickup": True
                },
            ],
        },
    ],
    "188": [
        {
            "Color": "white",
            "Text": "FLAWED EMERALD",
            "expressions": [
                {
                    "expression": "[name] >= chippedemerald && [name] <= perfectemerald",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == flawedemerald",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == emerald",
                    "should_pickup": False
                },
            ],
        },
        {
            "Color": "white",
            "Text": "FULL REJUVENATION POTION",
            "expressions": [
                {
                    "expression": "[name] == fullrejuvenationpotion",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == rejuvenationpotion",
                    "should_pickup": False
                },
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
                {
                    "expression": "[name] == festeringessenceofdestruction",
                    "should_pickup": True
                },
            ],
        },
    ],
    "191": [
        {
            "Color": "white",
            "Text": "REJUVENATION POTION",
            "expressions": [
                {
                    "expression": "[name] == fullrejuvenationpotion",
                    "should_pickup": False
                },
                {
                    "expression": "[name] == rejuvenationpotion",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "SUPER MANA POTION",
            "expressions": [
                {
                    "expression": "[name] == supermanapotion",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "SCROLL OF TOWN PORTAL",
            "expressions": [
                {
                    "expression": "[name] == scrolloftownportal",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "SCROLL OF IDENTIFY",
            "expressions": [
                {
                    "expression": "[name] == scrollofidentify",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "white",
            "Text": "SUPER HEALING POTION",
            "expressions": [
                {
                    "expression": "[name] == superhealingpotion",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "green",
            "Text": "RING",
            "expressions": [
                {
                    "expression": "[name] == ring && [quality] == set",
                    "should_pickup": True
                },
                {
                    "expression": "[type] == ring && [quality] == set # [hpregen] >= 2 && [maxhp] >= 15 // Angelic Halo",
                    "should_pickup": True
                },
            ],
        },
        {
            "Color": "orange",
            "Text": "SUR RUNE",
            "expressions": [
                {
                    "expression": "[name] >= elrune && [name] <= zodrune",
                    "should_pickup": True
                },
                {
                    "expression": "[name] == surrune",
                    "should_pickup": True
                },
            ],
        },
    ],
}