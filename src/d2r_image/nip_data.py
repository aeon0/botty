from d2r_image.data_models import ItemQuality, ItemQualityKeyword


NIP_RE_PATTERNS = {}
NIP_PATTERNS = {}

NTIP_ALIAS_QUALITY_MAP = {
    ItemQualityKeyword.LowQuality.value: 1,
    ItemQualityKeyword.Crude.value: 1,
    ItemQualityKeyword.Cracked.value: 1,
    ItemQuality.Gray.value: 2,
    ItemQuality.Normal.value: 2,
    ItemQualityKeyword.Superior.value: 3,
    ItemQuality.Magic.value: 4,
    ItemQuality.Set.value: 5,
    ItemQuality.Rare.value: 6,
    ItemQuality.Unique.value: 7,
    ItemQuality.Crafted.value: 8,
    ItemQuality.Runeword.value: 9,
    ItemQuality.Rune.value: 10,
}

NIP_ALIAS_STAT_PATTERNS = {
    "Adds {:d}-{:d} cold damage": [
        "54",
        "55"
    ],
    "Adds {:d}-{:d} damage": [
        "21",
        "22"
    ],
    "Adds {:d}-{:d} fire damage": [
        "48",
        "49"
    ],
    "Adds {:d}-{:d} lightning damage": [
        "50",
        "51"
    ],
    "Adds {:d}-{:d} magic damage": [
        "52",
        "53"
    ],
    "Adds {:d}-{:d} poison damage over {:d} seconds": [
        "57",
        "58",
		"59"
    ],
    "All Resistances {:d}": [
        ["39", "41", "43", "45"]
    ],
    "Attacker Takes Damage of {:d}": [
        "78"
    ],
    "Attacker Takes Damage of {:d} (Based on Character Level)": [
        "238"
    ],
    "Attacker Takes Lightning Damage of {:d}": [
        "128"
    ],
    "Cannot Be Frozen": [
        "153"
    ],
    "Cold Absorb {:d}": [
        "148",
    ],
    "Cold Resist {:d}": [
        "43"
    ],
    "Cold Resist {:d} (Based on Character Level)": [
        "230"
    ],
    "Damage Reduced by {:d}": [
        "34"
    ],
    "Damage Reduced by {:d}": [
        "36"
    ],
    "Damage {:d}": [
        "111"
    ],
    "Defense: {:d}": [
        "31"
    ],
    "Durability: {:d} of {:d}": [
        "72",
        "73"
    ],
    "Ethereal (Cannot be Repaired)": [
        "0x400000"
    ],
    "Extra Gold from Monsters {:d}": [
        "79"
    ],
    "Fire Absorb {:d}": [
        "142"
    ],
    "Fire Resist {:d}": [
        "39"
    ],
    "Fire Resist {:d} (Based on Character Level)": [
        "231"
    ],
    "Fires Explosive Arrows or Bolts": [
        "158"
    ],
    "Fires Magic Arrows": [
        "157"
    ],
    "Freezes target {:d}": [
        "134"
    ],
    "Half Freeze Duration": [
        "118"
    ],
    "Heal Stamina Plus {:d}": [
        "28"
    ],
    "Heal Stamina Plus {:d} (Based on Character Level)": [
        "241"
    ],
    "Hit Blinds Target {:d}": [
        "113"
    ],
    "Hit Causes Monster to Flee {:d}": [
        "112"
    ],
    "Ignore Target's Defense": [
        "116"
    ],
    "Increase Maximum Durability {:d}": [
        "75"
    ],
    "Increase Maximum Life {:d}": [
        "76"
    ],
    "Increase Maximum Mana {:d}": [
        "77"
    ],
    "Increased Stack Size": [
        "254"
    ],
    "Knockback": [
        "81"
    ],
    "Level {:d} {} ({:d}/{:d} Charges)": [
        "204"
    ],
    "Level {:d} {} Aura When Equipped": [
        "151"
    ],
    "Lightning Absorb {:d}": [
        "144"
    ],
    "Lightning Resist {:d}": [
        "41"
    ],
    "Lightning Resist {:d} (Based on Character Level)": [
        "232"
    ],
    "Magic Absorb {:d}": [
        "146"
    ],
    "Magic Damage Reduced by {:d}": [
        "35"
    ],
    "Magic Resist {:d}": [
        "37"
    ],
    "One-Hand Damage: {:d} to {:d}": [
        "21",
		"22"
    ],
    "Piercing Attack": [
        "156"
    ],
    "Poison Length Reduced by {:d}": [
        "110"
    ],
    "Poison Resist {:d}": [
        "45"
    ],
    "Poison Resist {:d} (Based on Character Level)": [
        "233"
    ],
    "Prevent Monster Heal": [
        "117"
    ],
    "Reduces all Vendor Prices {:d}": [
        "87"
    ],
    "Regenerate Mana {:d}": [
        "27"
    ],
    "Repairs {:d} durability {:d}": [
        "252"
    ],
    "Replenish Life {:d}": [
        "74"
    ],
    "Replenishes quantity": [
        "253"
    ],
    "Requirements {:d}": [
        "91"
    ],
    "Slain Monsters Rest in Peace": [
        "108"
    ],
    "Slows Target by {:d}": [
        "150"
    ],
    "Socketed ({:d})": [
        "194"
    ],
    "Throwable": [
        "125"
    ],
    "Two-Hand Damage: {:d} to {:d}": [
        "21",
		"22"
    ],
    "{:d} Absorbs Cold Damage": [
        "149",
    ],
    "{:d} Absorbs Cold Damage (Based on Character Level)": [
        "234"
    ],
    "{:d} Absorbs Fire Damage": [
        "143"
    ],
    "{:d} Absorbs Fire Damage (Based on Character Level)": [
        "235"
    ],
    "{:d} Absorbs Lightning Damage": [
        "145"
    ],
    "{:d} Absorbs Lightning Damage (Based on Character Level)": [
        "236"
    ],
    "{:d} Better Chance of Getting Magic Items": [
        "293"
    ],
    "{:d} Bonus to Attack Rating": [
        "279"
    ],
    "{:d} Chance of Crushing Blow": [
        "136"
    ],
    "{:d} Chance of Open Wounds": [
        "135"
    ],
    "{:d} Cold Absorb": [
        "149"
    ],
    "{:d} Damage to Demons": [
        "121"
    ],
    "{:d} Damage to Undead": [
        "122"
    ],
    "{:d} Deadly Strike": [
        "141"
    ],
    "{:d} Defense": [
        "31"
    ],
    "{:d} Defense (Based on Character Level)": [
        "214"
    ],
    "{:d} Defense vs. Melee": [
        "33"
    ],
    "{:d} Defense vs. Missile": [
        "32"
    ],
    "{:d} Enhanced Maximum Damage": [
        "219"
    ],
    "{:d} Fire Absorb": [
        "143"
    ],
    "{:d} Kick Damage": [
        "137"
    ],
    "{:d} Kick Damage (Based on Character Level)": [
        "249"
    ],
    "{:d} Life after each Demon Kill": [
        "139"
    ],
    "{:d} Life after each Kill": [
        "86"
    ],
    "{:d} Lightning Absorb": [
        "145"
    ],
    "{:d} Magic Absorb": [
        "147"
    ],
    "{:d} Maximum Stamina": [
        "11"
    ],
    "{:d} Maximum Stamina (Based on Character Level)": [
        "242"
    ],
    "{:d} cold damage": [
        "54"
    ],
    "{:d} damage": [
        "21"
    ],
    "{:d} fire damage": [
        "48"
    ],
    "{:d} lightning damage": [
        "50"
    ],
    "{:d} magic damage": [
        "52"
    ],
    "{:d} poison damage over {:d} seconds": [
        "57",
        "59"
    ],
    "{:d} to All Skills": [
        "127"
    ],
    "{:d} to Amazon Skill Levels": [
        "83,0"
    ],
    "{:d} to Assassin Skill Levels": [
        "83,6"
    ],
    "{:d} to Attack Rating": [
        "19"
    ],
    "{:d} to Attack Rating (Based on Character Level)": [
        "224"
    ],
    "{:d} to Attack Rating against Demons": [
        "123"
    ],
    "{:d} to Attack Rating against Demons (Based on Character Level)": [
        "245"
    ],
    "{:d} to Attack Rating against Undead": [
        "124"
    ],
    "{:d} to Attack Rating against Undead (Based on Character Level)": [
        "246"
    ],
    "{:d} to Attack Rating versus {}": [
        "180"
    ],
    "{:d} to Barbarian Skill Levels": [
        "83,4"
    ],
    "{:d} to Dexterity": [
        "2"
    ],
    "{:d} to Dexterity (Based on Character Level)": [
        "221"
    ],
    "{:d} to Druid Skill Levels": [
        "83,5"
    ],
    "{:d} to Energy": [
        "1"
    ],
    "{:d} to Energy (Based on Character Level)": [
        "222"
    ],
    "{:d} to Fire Skills": [
        "188"
    ],
    "{:d} to Life": [
        "7"
    ],
    "{:d} to Life (Based on Character Level)": [
        "216"
    ],
    "{:d} to Light Radius": [
        "89"
    ],
    "{:d} to Mana": [
        "9"
    ],
    "{:d} to Mana (Based on Character Level)": [
        "217"
    ],
    "{:d} to Mana after each Kill": [
        "138"
    ],
    "{:d} to Maximum Cold Damage": [
        "55"
    ],
    "{:d} to Maximum Cold Damage (Based on Character Level)": [
        "226"
    ],
    "{:d} to Maximum Damage": [
        "22"
    ],
    "{:d} to Maximum Damage (Based on Character Level)": [
        "218"
    ],
    "{:d} to Maximum Fire Damage": [
        "49"
    ],
    "{:d} to Maximum Fire Damage (Based on Character Level)": [
        "227"
    ],
    "{:d} to Maximum Lightning Damage": [
        "51"
    ],
    "{:d} to Maximum Lightning Damage (Based on Character Level)": [
        "228"
    ],
    "{:d} to Maximum Poison Damage": [
        "58"
    ],
    "{:d} to Maximum Poison Damage (Based on Character Level)": [
        "229"
    ],
    "{:d} to Minimum Cold Damage": [
        "54"
    ],
    "{:d} to Minimum Fire Damage": [
        "48"
    ],
    "{:d} to Minimum Lightning Damage": [
        "50"
    ],
    "{:d} to Minimum Poison Damage": [
        "57"
    ],
    "{:d} to Monster Defense Per Hit": [
        "120"
    ],
    "{:d} to Necromancer Skill Levels": [
        "83,2"
    ],
    "{:d} to Paladin Skill Levels": [
        "83,3"
    ],
    "{:d} to Sorceress Skill Levels": [
        "83,1"
    ],
    "{:d} to Strength": [
        "0"
    ],
    "{:d} to Strength (Based on Character Level)": [
        "220"
    ],
    "{:d} to Vitality": [
        "3"
    ],
    "{:d} to Vitality (Based on Character Level)": [
        "223"
    ],
    "{:d} to all Attributes": [
        ["0","1","2","3"]
    ],
    # "{:d} to {}": [
    #     "97"
    # ],
    "{:d} to Bow and Crossbow Skills (Amazon only)": [
        "188,0"
    ],
    "{:d} to Passive Skills (Amazon only)": [
        "188,1"
    ],
    "{:d} to Javelin and Spear Skills (Amazon only)": [
        "188,2"
    ],
    "{:d} to Fire Skills (Sorceress only)": [
        "188,8"
    ],
    "{:d} to Lightning Skills (Sorceress only)": [
        "188,9"
    ],
    "{:d} to Cold Skills (Sorceress only)": [
        "188,10"
    ],
    "{:d} to Curses (Necromancer only)": [
        "188,16"
    ],
    "{:d} to Poison and Bone Skills (Necromancer only)": [
        "188,17"
    ],
    "{:d} to Summoning Skills (Necromancer only)": [
        "188,18"
    ],
    "{:d} to Combat Skills (Paladin only)": [
        "188,24"
    ],
    "{:d} to Offensive Aura Skills (Paladin only)": [
        "188,25"
    ],
    "{:d} to Defensive Aura Skills (Paladin only)": [
        "188,26"
    ],
    "{:d} to Combat Skills (Barbarian only)": [
        "188,32"
    ],
    "{:d} to Masteries (Barbarian only)": [
        "188,33"
    ],
    "{:d} to Warcries (Barbarian only)": [
        "188,34"
    ],
    "{:d} to Summoning Skills (Druid only)": [
        "188,40"
    ],
    "{:d} to Shape Shifting Skills (Druid only)": [
        "188,41"
    ],
    "{:d} to Elemental Skills (Druid only)": [
        "188,42"
    ],
    "{:d} to Traps (Assassin only)": [
        "188,48"
    ],
    "{:d} to Shadow Disciplines (Assassin only)": [
        "188,49"
    ],
    "{:d} to Martial Arts (Assassin only)": [
        "188,50"
    ],
    "{:d} to Amazon Skill Levels": [
        "83,0"
    ],
    "{:d} to Sorceress Skill Levels": [
        "83,1"
    ],
    "{:d} to Necromancer Skill Levels": [
        "83,2"
    ],
    "{:d} to Paladin Skill Levels": [
        "83,3"
    ],
    "{:d} to Barbarian Skill Levels": [
        "83,4"
    ],
    "{:d} to Druid Skill Levels": [
        "83,5"
    ],
    "{:d} to Assassin Skill Levels": [
        "83,6"
    ],
    "{:d} Better Chance of Getting Magic Items": [
        "80"
    ],
    "{:d} Better Chance of Getting Magic Items (Based on Character Level)": [
        "240"
    ],
    "{:d} Bonus to Attack Rating": [
        "119"
    ],
    "{:d} Bonus to Attack Rating (Based on Character Level)": [
        "225"
    ],
    "{:d} Chance of Crushing Blow": [
        "136"
    ],
    "{:d} Chance of Crushing Blow (Based on Character Level)": [
        "247"
    ],
    "{:d} Chance of Open Wounds": [
        "135"
    ],
    "{:d} Chance of Open Wounds (Based on Character Level)": [
        "248"
    ],
    "{:d} Chance to cast level {:d} {} on attack": [
        "195"
    ],
    "{:d} Chance to cast level {:d} {} on striking": [
        "196"
    ],
    "{:d} Chance to cast level {:d} {} when struck": [
        "201"
    ],
    "{:d} Chance to cast level {:d} {} when you Die": [
        "197"
    ],
    "{:d} Chance to cast level {:d} {} when you Kill an Enemy": [
        "196"
    ],
    "{:d} Chance to cast level {:d} {} when you Level-Up": [
        "199"
    ],
    "{:d} Damage Taken Goes To Mana": [
        "114"
    ],
    "{:d} Damage to Demons": [
        "121"
    ],
    "{:d} Damage to Demons (Based on Character Level)": [
        "dmg-dem/lvl",
        "item_damage_demon_perlevel",
        "243"
    ],
    "{:d} Damage to Undead": [
        "122"
    ],
    "{:d} Damage to Undead (Based on Character Level)": [
        "244"
    ],
    "{:d} Deadly Strike": [
        "141"
    ],
    "{:d} Deadly Strike (Based on Character Level)": [
        "250"
    ],
    "{:d} Enhanced Defense": [
        "16"
    ],
    "{:d} Enhanced Defense (Based on Character Level)": [
        "215"
    ],
    "{:d} Enhanced Maximum Damage (Based on Character Level)": [
        "219"
    ],
    "{:d} Enhanced damage": [
        "18"
    ],
    "{:d} Extra Gold from Monsters": [
        "79"
    ],
    "{:d} Extra Gold from Monsters (Based on Character Level)": [
        "239"
    ],
    "{:d} Faster Block Rate": [
        "102"
    ],
    "{:d} Faster Cast Rate": [
        "105"
    ],
    "{:d} Faster Hit Recovery": [
        "99"
    ],
    "{:d} Faster Run/Walk": [
        "96"
    ],
    "{:d} Increased Attack Speed": [
        "93"
    ],
    "{:d} Increased Chance of Blocking": [
        "20"
    ],
    "{:d} Life stolen per hit": [
        "60"
    ],
    "{:d} Mana stolen per hit": [
        "62"
    ],
    "{:d} Reanimate as: {}": [
        "155"
    ],
    "{:d} Slower Stamina Drain": [
        "154"
    ],
    "{:d} Target Defense": [
        "116"
    ],
    "{:d} to Cold Skill Damage": [
        "331"
    ],
    "{:d} to Enemy Cold Resistance": [
        "335"
    ],
    "{:d} to Enemy Fire Resistance": [
        "333"
    ],
    "{:d} to Enemy Lightning Resistance": [
        "334"
    ],
    "{:d} to Enemy Poison Resistance": [
        "336"
    ],
    "{:d} to Experience Gained": [
        "85"
    ],
    "{:d} to Fire Skill Damage": [
        "329"
    ],
    "{:d} to Lightning Skill Damage": [
        "330"
    ],
    "{:d} to Maximum Cold Resist": [
        "44"
    ],
    "{:d} to Maximum Fire Resist": [
        "40"
    ],
    "{:d} to Maximum Lightning Resist": [
        "42"
    ],
    "{:d} to Maximum Magic Resist": [
        "38"
    ],
    "{:d} to Maximum Poison Resist": [
        "46"
    ],
    "{:d} to Poison Skill Damage": [
        "332"
    ]
}