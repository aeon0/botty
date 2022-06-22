from d2r_image.data_models import ItemQuality, ItemQualityKeyword


NTIP_ALIAS_QUALITY_MAP = {
    ItemQualityKeyword.LowQuality.value: 1,
    ItemQualityKeyword.Crude.value: 1,
    ItemQualityKeyword.Cracked.value: 1,
    ItemQuality.LowQuality.value: 1,
    ItemQuality.Crude.value: 1,
    ItemQuality.Cracked.value: 1,
    ItemQuality.Gray.value: 2,
    ItemQuality.Normal.value: 2,
    ItemQuality.Superior.value: 3,
    ItemQualityKeyword.Superior.value: 3,
    ItemQuality.Magic.value: 4,
    ItemQuality.Set.value: 5,
    ItemQuality.Rare.value: 6,
    ItemQuality.Unique.value: 7,
    ItemQuality.Crafted.value: 8,
    ItemQuality.Runeword.value: 9,
    ItemQuality.Rune.value: 10,
}

"""
ITEM PROPERTIES THAT MAP TO STATS RATHER THAN A READ PROPERTY
['itemskillonattack']='195'
['itemskillonkill']='196'
['itemskillondeath']='197'
['itemskillonhit']='198'
['itemskillonlevelup']='199'
['itemskillongethit']='201'
['itemchargedskill']='204'
['itemnonclassskill']='97' (not sure how this is used)
['itemsingleskill']='107' doesn't map to skill
['itemaddskilltab']='188' doesn't map to skill
"""
PROPS_TO_SKILLID = {195, 196, 197, 198, 199, 201, 204}

BNIP_ALIAS_STAT_PATTERNS = {
    "{:d} Defense": [
        "5006"
    ],
    "{:d} Defense vs. Missile": [
        "32"
    ],
    "{:d} Defense vs. Melee": [
        "33"
    ],
    "Damage Reduced by {:d}": [
        "34"
    ],
    "Damage Reduced by {:d}%": [
        "36"
    ],
    "{:d}% Enhanced Defense": [
        "16"
    ],
    "Magic Damage Reduced by {:d}": [
        "35"
    ],
    "{:d} to Strength": [
        "0"
    ],
    "{:d} to Dexterity": [
        "2"
    ],
    "{:d} to Vitality": [
        "3"
    ],
    "{:d} to Energy": [
        "1"
    ],
    "{:d} to Mana": [
        [
            "8",
            "9"
        ]
    ],
    "Increase Maximum Mana {:d}%": [
        "77"
    ],
    "{:d} to Life": [
        [
            "6",
            "7"
        ]
    ],
    "Increase Maximum Life {:d}%": [
        "76"
    ],
    "{:d} to Attack Rating": [
        "19"
    ],
    "{:d}% Increased Chance of Blocking": [
        "20"
    ],
    "{:d} to Minimum Cold Damage": [
        "54"
    ],
    "{:d} to Maximum Cold Damage": [
        "55"
    ],
    "{:d} to Minimum Fire Damage": [
        "48"
    ],
    "{:d} to Maximum Fire Damage": [
        "49"
    ],
    "{:d} to Minimum Lightning Damage": [
        "50"
    ],
    "{:d} to Maximum Lightning Damage": [
        "51"
    ],
    "{:d} to Minimum Poison Damage": [
        "57"
    ],
    "{:d} to Maximum Poison Damage": [
        "58"
    ],
    "{:d} to Minimum Damage": [
        "21"
    ],
    "{:d} to Maximum Damage": [
        "22"
    ],
    "{:d}% Damage Taken Goes To Mana": [
        "114"
    ],
    "Fire Resist {:d}%": [
        "39"
    ],
    "{:d}% to Maximum Fire Resist": [
        "40"
    ],
    "Lightning Resist {:d}%": [
        "41"
    ],
    "{:d}% to Maximum Lightning Resist": [
        "42"
    ],
    "Cold Resist {:d}%": [
        "43"
    ],
    "{:d}% to Maximum Cold Resist": [
        "44"
    ],
    "Magic Resist {:d}%": [
        "37"
    ],
    "{:d}% to Maximum Magic Resist": [
        "38"
    ],
    "Poison Resist {:d}%": [
        "45"
    ],
    "{:d}% to Maximum Poison Resist": [
        "46"
    ],
    "All Resistances {:d}": [
        [
            "6969",
            "39",
            "41",
            "43",
            "45"
        ]
    ],
    "{:d} Fire Absorb": [
        "143"
    ],
    "Fire Absorb {:d}%": [
        "142"
    ],
    "{:d} Lightning Absorb": [
        "145"
    ],
    "Lightning Absorb {:d}%": [
        "144"
    ],
    "{:d} Magic Absorb": [
        "147"
    ],
    "Magic Absorb {:d}%": [
        "146"
    ],
    "{:d} Cold Absorb": [
        "149"
    ],
    "Cold Absorb {:d}%": [
        "148"
    ],
    "Durability: {:d} of {:d}": [
        "72",
        "73"
    ],
    "Increase Maximum Durability {:d}%": [
        "75"
    ],
    "Replenish Life {:d}": [
        "74"
    ],
    "Attacker Takes Damage of {:d}": [
        "78"
    ],
    "{:d}% Increased Attack Speed": [
        "93"
    ],
    "{:d}% Extra Gold from Monsters": [
        "79"
    ],
    "{:d}% Better Chance of Getting Magic Items": [
        "80"
    ],
    "Knockback": [
        "81"
    ],
    "Heal Stamina Plus {:d}%": [
        "28"
    ],
    "Regenerate Mana {:d}%": [
        "27"
    ],
    "{:d} Maximum Stamina": [
        [
            "10",
            "11"
        ]
    ],
    "{:d}% Mana stolen per hit": [
        "62"
    ],
    "{:d}% Life stolen per hit": [
        "60"
    ],
    "{:d} to Amazon Skill Levels": [
        "83,0"
    ],
    "{:d} to Paladin Skill Levels": [
        "83,3"
    ],
    "{:d} to Necromancer Skill Levels": [
        "83,2"
    ],
    "{:d} to Sorceress Skill Levels": [
        "83,1"
    ],
    "{:d} to Barbarian Skill Levels": [
        "83,4"
    ],
    "{:d} to Light Radius": [
        "89"
    ],
    "Requirements {:d}%": [
        "91"
    ],
    "{:d}% Faster Run/Walk": [
        "96"
    ],
    "{:d}% Faster Hit Recovery": [
        "99"
    ],
    "{:d}% Faster Block Rate": [
        "102"
    ],
    "{:d}% Faster Cast Rate": [
        "105"
    ],
    "Poison Length Reduced by {:d}%": [
        "110"
    ],
    "Damage {:d}": [
        "111"
    ],
    "Hit Causes Monster to Flee {:d}%": [
        "112"
    ],
    "Hit Blinds Target {:d}": [
        "113"
    ],
    "Ignore Target's Defense": [
        "115"
    ],
    "{:d}% Target Defense": [
        "116"
    ],
    "Prevent Monster Heal": [
        "117"
    ],
    "Half Freeze Duration": [
        "118"
    ],
    "{:d}% Bonus to Attack Rating": [
        "119"
    ],
    "{:d} to Monster Defense Per Hit": [
        "120"
    ],
    "{:d}% Damage to Demons": [
        "121"
    ],
    "{:d}% Damage to Undead": [
        "122"
    ],
    "{:d} to Attack Rating against Demons": [
        "123"
    ],
    "{:d} to Attack Rating against Undead": [
        "124"
    ],
    "{:d} to Fire Skills": [
        "126"
    ],
    "{:d} to All Skills": [
        "127"
    ],
    "Attacker Takes Lightning Damage of {:d}": [
        "128"
    ],
    "Freezes Target {:d}": [
        "134"
    ],
    "{:d}% Chance of Open Wounds": [
        "135"
    ],
    "{:d}% Chance of Crushing Blow": [
        "136"
    ],
    "{:d} Kick Damage": [
        "137"
    ],
    "{:d} to Mana after each Kill": [
        "138"
    ],
    "{:d} Life after each Demon Kill": [
        "139"
    ],
    "{:d}% Deadly Strike": [
        "141"
    ],
    "Slows Target by {:d}%": [
        "150"
    ],
    "Cannot Be Frozen": [
        "153"
    ],
    "{:d}% Slower Stamina Drain": [
        "154"
    ],
    "Reanimate As: [Returned]": [
        "155"
    ],
    "Piercing Attack": [
        "156"
    ],
    "Fires Magic Arrows": [
        "157"
    ],
    "Fires Explosive Arrows or Bolts": [
        "158"
    ],
    "{:d} to Druid Skill Levels": [
        "83,5"
    ],
    "{:d} to Assassin Skill Levels": [
        "83,6"
    ],
    "{:d} to Magic Arrow (Amazon only)": [
        "107,6"
    ],
    "{:d} to Fire Arrow (Amazon only)": [
        "107,7"
    ],
    "{:d} to Inner Sight (Amazon only)": [
        "107,8"
    ],
    "{:d} to Critical Strike (Amazon only)": [
        "107,9"
    ],
    "{:d} to Jab (Amazon only)": [
        "107,10"
    ],
    "{:d} to Cold Arrow (Amazon only)": [
        "107,11"
    ],
    "{:d} to Multiple Shot (Amazon only)": [
        "107,12"
    ],
    "{:d} to Dodge (Amazon only)": [
        "107,13"
    ],
    "{:d} to Power Strike (Amazon only)": [
        "107,14"
    ],
    "{:d} to Poison Javelin (Amazon only)": [
        "107,15"
    ],
    "{:d} to Exploding Arrow (Amazon only)": [
        "107,16"
    ],
    "{:d} to Slow Missiles (Amazon only)": [
        "107,17"
    ],
    "{:d} to Avoid (Amazon only)": [
        "107,18"
    ],
    "{:d} to Impale (Amazon only)": [
        "107,19"
    ],
    "{:d} to Lightning Bolt (Amazon only)": [
        "107,20"
    ],
    "{:d} to Ice Arrow (Amazon only)": [
        "107,21"
    ],
    "{:d} to Guided Arrow (Amazon only)": [
        "107,22"
    ],
    "{:d} to Penetrate (Amazon only)": [
        "107,23"
    ],
    "{:d} to Charged Strike (Amazon only)": [
        "107,24"
    ],
    "{:d} to Plague Javelin (Amazon only)": [
        "107,25"
    ],
    "{:d} to Strafe (Amazon only)": [
        "107,26"
    ],
    "{:d} to Immolation Arrow (Amazon only)": [
        "107,27"
    ],
    "{:d} to Decoy (Amazon only)": [
        "107,28"
    ],
    "{:d} to Evade (Amazon only)": [
        "107,29"
    ],
    "{:d} to Fend (Amazon only)": [
        "107,30"
    ],
    "{:d} to Freezing Arrow (Amazon only)": [
        "107,31"
    ],
    "{:d} to Valkyrie (Amazon only)": [
        "107,32"
    ],
    "{:d} to Pierce (Amazon only)": [
        "107,33"
    ],
    "{:d} to Lightning Strike (Amazon only)": [
        "107,34"
    ],
    "{:d} to Lightning Fury (Amazon only)": [
        "107,35"
    ],
    "{:d} to Fire Bolt (Sorceress only)": [
        "107,36"
    ],
    "{:d} to Warmth (Sorceress only)": [
        "107,37"
    ],
    "{:d} to Charged Bolt (Sorceress only)": [
        "107,38"
    ],
    "{:d} to Ice Bolt (Sorceress only)": [
        "107,39"
    ],
    "{:d} to Frozen Armor (Sorceress only)": [
        "107,40"
    ],
    "{:d} to Inferno (Sorceress only)": [
        "107,41"
    ],
    "{:d} to Static Field (Sorceress only)": [
        "107,42"
    ],
    "{:d} to Telekinesis (Sorceress only)": [
        "107,43"
    ],
    "{:d} to Frost Nova (Sorceress only)": [
        "107,44"
    ],
    "{:d} to Ice Blast (Sorceress only)": [
        "107,45"
    ],
    "{:d} to Blaze (Sorceress only)": [
        "107,46"
    ],
    "{:d} to Fire Ball (Sorceress only)": [
        "107,47"
    ],
    "{:d} to Nova (Sorceress only)": [
        "107,48"
    ],
    "{:d} to Lightning (Sorceress only)": [
        "107,49"
    ],
    "{:d} to Shiver Armor (Sorceress only)": [
        "107,50"
    ],
    "{:d} to Fire Wall (Sorceress only)": [
        "107,51"
    ],
    "{:d} to Enchant (Sorceress only)": [
        "107,52"
    ],
    "{:d} to Chain Lightning (Sorceress only)": [
        "107,53"
    ],
    "{:d} to Teleport (Sorceress only)": [
        "107,54"
    ],
    "{:d} to Glacial Spike (Sorceress only)": [
        "107,55"
    ],
    "{:d} to Meteor (Sorceress only)": [
        "107,56"
    ],
    "{:d} to Thunder Storm (Sorceress only)": [
        "107,57"
    ],
    "{:d} to Energy Shield (Sorceress only)": [
        "107,58"
    ],
    "{:d} to Blizzard (Sorceress only)": [
        "107,59"
    ],
    "{:d} to Chilling Armor (Sorceress only)": [
        "107,60"
    ],
    "{:d} to Fire Mastery (Sorceress only)": [
        "107,61"
    ],
    "{:d} to Hydra (Sorceress only)": [
        "107,62"
    ],
    "{:d} to Lightning Mastery (Sorceress only)": [
        "107,63"
    ],
    "{:d} to Frozen Orb (Sorceress only)": [
        "107,64"
    ],
    "{:d} to Cold Mastery (Sorceress only)": [
        "107,65"
    ],
    "{:d} to Amplify Damage (Necromancer only)": [
        "107,66"
    ],
    "{:d} to Teeth (Necromancer only)": [
        "107,67"
    ],
    "{:d} to Bone Armor (Necromancer only)": [
        "107,68"
    ],
    "{:d} to Skeleton Mastery (Necromancer only)": [
        "107,69"
    ],
    "{:d} to Raise Skeleton (Necromancer only)": [
        "107,70"
    ],
    "{:d} to Dim Vision (Necromancer only)": [
        "107,71"
    ],
    "{:d} to Weaken (Necromancer only)": [
        "107,72"
    ],
    "{:d} to Poison Dagger (Necromancer only)": [
        "107,73"
    ],
    "{:d} to Corpse Explosion (Necromancer only)": [
        "107,74"
    ],
    "{:d} to Clay Golem (Necromancer only)": [
        "107,75"
    ],
    "{:d} to Iron Maiden (Necromancer only)": [
        "107,76"
    ],
    "{:d} to Terror (Necromancer only)": [
        "107,77"
    ],
    "{:d} to Bone Wall (Necromancer only)": [
        "107,78"
    ],
    "{:d} to Golem Mastery (Necromancer only)": [
        "107,79"
    ],
    "{:d} to Raise Skeletal Mage (Necromancer only)": [
        "107,80"
    ],
    "{:d} to Confuse (Necromancer only)": [
        "107,81"
    ],
    "{:d} to Life Tap (Necromancer only)": [
        "107,82"
    ],
    "{:d} to Poison Explosion (Necromancer only)": [
        "107,83"
    ],
    "{:d} to Bone Spear (Necromancer only)": [
        "107,84"
    ],
    "{:d} to Blood Golem (Necromancer only)": [
        "107,85"
    ],
    "{:d} to Attract (Necromancer only)": [
        "107,86"
    ],
    "{:d} to Decrepify (Necromancer only)": [
        "107,87"
    ],
    "{:d} to Bone Prison (Necromancer only)": [
        "107,88"
    ],
    "{:d} to Summon Resist (Necromancer only)": [
        "107,89"
    ],
    "{:d} to Iron Golem (Necromancer only)": [
        "107,90"
    ],
    "{:d} to Lower Resist (Necromancer only)": [
        "107,91"
    ],
    "{:d} to Poison Nova (Necromancer only)": [
        "107,92"
    ],
    "{:d} to Bone Spirit (Necromancer only)": [
        "107,93"
    ],
    "{:d} to Fire Golem (Necromancer only)": [
        "107,94"
    ],
    "{:d} to Revive (Necromancer only)": [
        "107,95"
    ],
    "{:d} to Sacrifice (Paladin only)": [
        "107,96"
    ],
    "{:d} to Smite (Paladin only)": [
        "107,97"
    ],
    "{:d} to Might (Paladin only)": [
        "107,98"
    ],
    "{:d} to Prayer (Paladin only)": [
        "107,99"
    ],
    "{:d} to Resist Fire (Paladin only)": [
        "107,100"
    ],
    "{:d} to Holy Bolt (Paladin only)": [
        "107,101"
    ],
    "{:d} to Holy Fire (Paladin only)": [
        "107,102"
    ],
    "{:d} to Thorns (Paladin only)": [
        "107,103"
    ],
    "{:d} to Defiance (Paladin only)": [
        "107,104"
    ],
    "{:d} to Resist Cold (Paladin only)": [
        "107,105"
    ],
    "{:d} to Zeal (Paladin only)": [
        "107,106"
    ],
    "{:d} to Charge (Paladin only)": [
        "107,107"
    ],
    "{:d} to Blessed Aim (Paladin only)": [
        "107,108"
    ],
    "{:d} to Cleansing (Paladin only)": [
        "107,109"
    ],
    "{:d} to Resist Lightning (Paladin only)": [
        "107,110"
    ],
    "{:d} to Vengeance (Paladin only)": [
        "107,111"
    ],
    "{:d} to Blessed Hammer (Paladin only)": [
        "107,112"
    ],
    "{:d} to Concentration (Paladin only)": [
        "107,113"
    ],
    "{:d} to Holy Freeze (Paladin only)": [
        "107,114"
    ],
    "{:d} to Vigor (Paladin only)": [
        "107,115"
    ],
    "{:d} to Conversion (Paladin only)": [
        "107,116"
    ],
    "{:d} to Holy Shield (Paladin only)": [
        "107,117"
    ],
    "{:d} to Holy Shock (Paladin only)": [
        "107,118"
    ],
    "{:d} to Sanctuary (Paladin only)": [
        "107,119"
    ],
    "{:d} to Meditation (Paladin only)": [
        "107,120"
    ],
    "{:d} to Fist of the Heavens (Paladin only)": [
        "107,121"
    ],
    "{:d} to Fanaticism (Paladin only)": [
        "107,122"
    ],
    "{:d} to Conviction (Paladin only)": [
        "107,123"
    ],
    "{:d} to Redemption (Paladin only)": [
        "107,124"
    ],
    "{:d} to Salvation (Paladin only)": [
        "107,125"
    ],
    "{:d} to Bash (Barbarian only)": [
        "107,126"
    ],
    "{:d} to Blade Mastery (Barbarian only)": [
        "107,127"
    ],
    "{:d} to Axe Mastery (Barbarian only)": [
        "107,128"
    ],
    "{:d} to Mace Mastery (Barbarian only)": [
        "107,129"
    ],
    "{:d} to Howl (Barbarian only)": [
        "107,130"
    ],
    "{:d} to Find Potion (Barbarian only)": [
        "107,131"
    ],
    "{:d} to Leap (Barbarian only)": [
        "107,132"
    ],
    "{:d} to Double Swing (Barbarian only)": [
        "107,133"
    ],
    "{:d} to Polearm Mastery (Barbarian only)": [
        "107,134"
    ],
    "{:d} to Throwing Mastery (Barbarian only)": [
        "107,135"
    ],
    "{:d} to Spear Mastery (Barbarian only)": [
        "107,136"
    ],
    "{:d} to Taunt (Barbarian only)": [
        "107,137"
    ],
    "{:d} to Shout (Barbarian only)": [
        "107,138"
    ],
    "{:d} to Stun (Barbarian only)": [
        "107,139"
    ],
    "{:d} to Double Throw (Barbarian only)": [
        "107,140"
    ],
    "{:d} to Increased Stamina (Barbarian only)": [
        "107,141"
    ],
    "{:d} to Find Item (Barbarian only)": [
        "107,142"
    ],
    "{:d} to Leap Attack (Barbarian only)": [
        "107,143"
    ],
    "{:d} to Concentrate (Barbarian only)": [
        "107,144"
    ],
    "{:d} to Iron Skin (Barbarian only)": [
        "107,145"
    ],
    "{:d} to Battle Cry (Barbarian only)": [
        "107,146"
    ],
    "{:d} to Frenzy (Barbarian only)": [
        "107,147"
    ],
    "{:d} to Increased Speed (Barbarian only)": [
        "107,148"
    ],
    "{:d} to Battle Orders (Barbarian only)": [
        "107,149"
    ],
    "{:d} to Grim Ward (Barbarian only)": [
        "107,150"
    ],
    "{:d} to Whirlwind (Barbarian only)": [
        "107,151"
    ],
    "{:d} to Berserk (Barbarian only)": [
        "107,152"
    ],
    "{:d} to Natural Resistance (Barbarian only)": [
        "107,153"
    ],
    "{:d} to War Cry (Barbarian only)": [
        "107,154"
    ],
    "{:d} to Battle Command (Barbarian only)": [
        "107,155"
    ],
    "{:d} to Raven (Druid only)": [
        "107,221"
    ],
    "{:d} to Poison Creeper (Druid only)": [
        "107,222"
    ],
    "{:d} to Werewolf (Druid only)": [
        "107,223"
    ],
    "{:d} to Lycanthropy (Druid only)": [
        "107,224"
    ],
    "{:d} to Firestorm (Druid only)": [
        "107,225"
    ],
    "{:d} to Oak Sage (Druid only)": [
        "107,226"
    ],
    "{:d} to Summon Spirit Wolf (Druid only)": [
        "107,227"
    ],
    "{:d} to Werebear (Druid only)": [
        "107,228"
    ],
    "{:d} to Molten Boulder (Druid only)": [
        "107,229"
    ],
    "{:d} to Arctic Blast (Druid only)": [
        "107,230"
    ],
    "{:d} to Carrion Vine (Druid only)": [
        "107,231"
    ],
    "{:d} to Feral Rage (Druid only)": [
        "107,232"
    ],
    "{:d} to Maul (Druid only)": [
        "107,233"
    ],
    "{:d} to Fissure (Druid only)": [
        "107,234"
    ],
    "{:d} to Cyclone Armor (Druid only)": [
        "107,235"
    ],
    "{:d} to Heart of Wolverine (Druid only)": [
        "107,236"
    ],
    "{:d} to Summon Dire Wolf (Druid only)": [
        "107,237"
    ],
    "{:d} to Rabies (Druid only)": [
        "107,238"
    ],
    "{:d} to Fire Claws (Druid only)": [
        "107,239"
    ],
    "{:d} to Twister (Druid only)": [
        "107,240"
    ],
    "{:d} to Solar Creeper (Druid only)": [
        "107,241"
    ],
    "{:d} to Hunger (Druid only)": [
        "107,242"
    ],
    "{:d} to Shock Wave (Druid only)": [
        "107,243"
    ],
    "{:d} to Volcano (Druid only)": [
        "107,244"
    ],
    "{:d} to Tornado (Druid only)": [
        "107,245"
    ],
    "{:d} to Spirit of Barbs (Druid only)": [
        "107,246"
    ],
    "{:d} to Summon Grizzly (Druid only)": [
        "107,247"
    ],
    "{:d} to Fury (Druid only)": [
        "107,248"
    ],
    "{:d} to Armageddon (Druid only)": [
        "107,249"
    ],
    "{:d} to Hurricane (Druid only)": [
        "107,250"
    ],
    "{:d} to Fire Blast (Assassin only)": [
        "107,251"
    ],
    "{:d} to Claw Mastery (Assassin only)": [
        "107,252"
    ],
    "{:d} to Psychic Hammer (Assassin only)": [
        "107,253"
    ],
    "{:d} to Tiger Strike (Assassin only)": [
        "107,254"
    ],
    "{:d} to Dragon Talon (Assassin only)": [
        "107,255"
    ],
    "{:d} to Shock Web (Assassin only)": [
        "107,256"
    ],
    "{:d} to Blade Sentinel (Assassin only)": [
        "107,257"
    ],
    "{:d} to Burst of Speed (Assassin only)": [
        "107,258"
    ],
    "{:d} to Fists of Fire (Assassin only)": [
        "107,259"
    ],
    "{:d} to Dragon Claw (Assassin only)": [
        "107,260"
    ],
    "{:d} to Charged Bolt Sentry (Assassin only)": [
        "107,261"
    ],
    "{:d} to Wake of Fire (Assassin only)": [
        "107,262"
    ],
    "{:d} to Weapon Block (Assassin only)": [
        "107,263"
    ],
    "{:d} to Cloak of Shadows (Assassin only)": [
        "107,264"
    ],
    "{:d} to Cobra Strike (Assassin only)": [
        "107,265"
    ],
    "{:d} to Blade Fury (Assassin only)": [
        "107,266"
    ],
    "{:d} to Fade (Assassin only)": [
        "107,267"
    ],
    "{:d} to Shadow Warrior (Assassin only)": [
        "107,268"
    ],
    "{:d} to Claws of Thunder (Assassin only)": [
        "107,269"
    ],
    "{:d} to Dragon Tail (Assassin only)": [
        "107,270"
    ],
    "{:d} to Lightning Sentry (Assassin only)": [
        "107,271"
    ],
    "{:d} to Wake of Inferno (Assassin only)": [
        "107,272"
    ],
    "{:d} to Mind Blast (Assassin only)": [
        "107,273"
    ],
    "{:d} to Blades of Ice (Assassin only)": [
        "107,274"
    ],
    "{:d} to Dragon Flight (Assassin only)": [
        "107,275"
    ],
    "{:d} to Death Sentry (Assassin only)": [
        "107,276"
    ],
    "{:d} to Blade Shield (Assassin only)": [
        "107,277"
    ],
    "{:d} to Venom (Assassin only)": [
        "107,278"
    ],
    "{:d} to Shadow Master (Assassin only)": [
        "107,279"
    ],
    "{:d} to Phoenix Strike (Assassin only)": [
        "107,280"
    ],
    "{:d} to Bow and Crossbow Skills (Amazon Only)": [
        "188,0"
    ],
    "{:d} to Passive and Magic Skills (Amazon Only)": [
        "188,1"
    ],
    "{:d} to Javelin and Spear Skills (Amazon Only)": [
        "188,2"
    ],
    "{:d} to Fire Skills (Sorceress Only)": [
        "188,3"
    ],
    "{:d} to Lightning Skills (Sorceress Only)": [
        "188,4"
    ],
    "{:d} to Cold Skills (Sorceress Only)": [
        "188,5"
    ],
    "{:d} to Curses (Necromancer Only)": [
        "188,6"
    ],
    "{:d} to Poison and Bone Skills (Necromancer Only)": [
        "188,7"
    ],
    "{:d} to Combat Skills (Necromancer Only)": [
        "188,8"
    ],
    "{:d} to Combat Skills (Paladin Only)": [
        "188,9"
    ],
    "{:d} to Offensive Auras (Paladin Only)": [
        "188,10"
    ],
    "{:d} to Defensive Auras (Paladin Only)": [
        "188,11"
    ],
    "{:d} to Combat Skills (Barbarian Only)": [
        "188,12"
    ],
    "{:d} to Masteries (Barbarian Only)": [
        "188,13"
    ],
    "{:d} to Warcries (Barbarian Only)": [
        "188,14"
    ],
    "{:d} to Summoning Skills (Druid Only)": [
        "188,15"
    ],
    "{:d} to Shape Shifting Skills (Druid Only)": [
        "188,16"
    ],
    "{:d} to Elemental Skills (Druid Only)": [
        "188,17"
    ],
    "{:d} to Traps (Assassin Only)": [
        "188,18"
    ],
    "{:d} to Shadow Disciplines (Assassin Only)": [
        "188,19"
    ],
    "{:d} to Martial Arts (Assassin Only)": [
        "188,20"
    ],
    "Level {:d} Magic Arrow Aura When Equipped": [
        "151,6"
    ],
    "Level {:d} Fire Arrow Aura When Equipped": [
        "151,7"
    ],
    "Level {:d} Inner Sight Aura When Equipped": [
        "151,8"
    ],
    "Level {:d} Critical Strike Aura When Equipped": [
        "151,9"
    ],
    "Level {:d} Jab Aura When Equipped": [
        "151,10"
    ],
    "Level {:d} Cold Arrow Aura When Equipped": [
        "151,11"
    ],
    "Level {:d} Multiple Shot Aura When Equipped": [
        "151,12"
    ],
    "Level {:d} Dodge Aura When Equipped": [
        "151,13"
    ],
    "Level {:d} Power Strike Aura When Equipped": [
        "151,14"
    ],
    "Level {:d} Poison Javelin Aura When Equipped": [
        "151,15"
    ],
    "Level {:d} Exploding Arrow Aura When Equipped": [
        "151,16"
    ],
    "Level {:d} Slow Missiles Aura When Equipped": [
        "151,17"
    ],
    "Level {:d} Avoid Aura When Equipped": [
        "151,18"
    ],
    "Level {:d} Impale Aura When Equipped": [
        "151,19"
    ],
    "Level {:d} Lightning Bolt Aura When Equipped": [
        "151,20"
    ],
    "Level {:d} Ice Arrow Aura When Equipped": [
        "151,21"
    ],
    "Level {:d} Guided Arrow Aura When Equipped": [
        "151,22"
    ],
    "Level {:d} Penetrate Aura When Equipped": [
        "151,23"
    ],
    "Level {:d} Charged Strike Aura When Equipped": [
        "151,24"
    ],
    "Level {:d} Plague Javelin Aura When Equipped": [
        "151,25"
    ],
    "Level {:d} Strafe Aura When Equipped": [
        "151,26"
    ],
    "Level {:d} Immolation Arrow Aura When Equipped": [
        "151,27"
    ],
    "Level {:d} Decoy Aura When Equipped": [
        "151,28"
    ],
    "Level {:d} Evade Aura When Equipped": [
        "151,29"
    ],
    "Level {:d} Fend Aura When Equipped": [
        "151,30"
    ],
    "Level {:d} Freezing Arrow Aura When Equipped": [
        "151,31"
    ],
    "Level {:d} Valkyrie Aura When Equipped": [
        "151,32"
    ],
    "Level {:d} Pierce Aura When Equipped": [
        "151,33"
    ],
    "Level {:d} Lightning Strike Aura When Equipped": [
        "151,34"
    ],
    "Level {:d} Lightning Fury Aura When Equipped": [
        "151,35"
    ],
    "Level {:d} Fire Bolt Aura When Equipped": [
        "151,36"
    ],
    "Level {:d} Warmth Aura When Equipped": [
        "151,37"
    ],
    "Level {:d} Charged Bolt Aura When Equipped": [
        "151,38"
    ],
    "Level {:d} Ice Bolt Aura When Equipped": [
        "151,39"
    ],
    "Level {:d} Frozen Armor Aura When Equipped": [
        "151,40"
    ],
    "Level {:d} Inferno Aura When Equipped": [
        "151,41"
    ],
    "Level {:d} Static Field Aura When Equipped": [
        "151,42"
    ],
    "Level {:d} Telekinesis Aura When Equipped": [
        "151,43"
    ],
    "Level {:d} Frost Nova Aura When Equipped": [
        "151,44"
    ],
    "Level {:d} Ice Blast Aura When Equipped": [
        "151,45"
    ],
    "Level {:d} Blaze Aura When Equipped": [
        "151,46"
    ],
    "Level {:d} Fire Ball Aura When Equipped": [
        "151,47"
    ],
    "Level {:d} Nova Aura When Equipped": [
        "151,48"
    ],
    "Level {:d} Lightning Aura When Equipped": [
        "151,49"
    ],
    "Level {:d} Shiver Armor Aura When Equipped": [
        "151,50"
    ],
    "Level {:d} Fire Wall Aura When Equipped": [
        "151,51"
    ],
    "Level {:d} Enchant Aura When Equipped": [
        "151,52"
    ],
    "Level {:d} Chain Lightning Aura When Equipped": [
        "151,53"
    ],
    "Level {:d} Teleport Aura When Equipped": [
        "151,54"
    ],
    "Level {:d} Glacial Spike Aura When Equipped": [
        "151,55"
    ],
    "Level {:d} Meteor Aura When Equipped": [
        "151,56"
    ],
    "Level {:d} Thunder Storm Aura When Equipped": [
        "151,57"
    ],
    "Level {:d} Energy Shield Aura When Equipped": [
        "151,58"
    ],
    "Level {:d} Blizzard Aura When Equipped": [
        "151,59"
    ],
    "Level {:d} Chilling Armor Aura When Equipped": [
        "151,60"
    ],
    "Level {:d} Fire Mastery Aura When Equipped": [
        "151,61"
    ],
    "Level {:d} Hydra Aura When Equipped": [
        "151,62"
    ],
    "Level {:d} Lightning Mastery Aura When Equipped": [
        "151,63"
    ],
    "Level {:d} Frozen Orb Aura When Equipped": [
        "151,64"
    ],
    "Level {:d} Cold Mastery Aura When Equipped": [
        "151,65"
    ],
    "Level {:d} Amplify Damage Aura When Equipped": [
        "151,66"
    ],
    "Level {:d} Teeth Aura When Equipped": [
        "151,67"
    ],
    "Level {:d} Bone Armor Aura When Equipped": [
        "151,68"
    ],
    "Level {:d} Skeleton Mastery Aura When Equipped": [
        "151,69"
    ],
    "Level {:d} Raise Skeleton Aura When Equipped": [
        "151,70"
    ],
    "Level {:d} Dim Vision Aura When Equipped": [
        "151,71"
    ],
    "Level {:d} Weaken Aura When Equipped": [
        "151,72"
    ],
    "Level {:d} Poison Dagger Aura When Equipped": [
        "151,73"
    ],
    "Level {:d} Corpse Explosion Aura When Equipped": [
        "151,74"
    ],
    "Level {:d} Clay Golem Aura When Equipped": [
        "151,75"
    ],
    "Level {:d} Iron Maiden Aura When Equipped": [
        "151,76"
    ],
    "Level {:d} Terror Aura When Equipped": [
        "151,77"
    ],
    "Level {:d} Bone Wall Aura When Equipped": [
        "151,78"
    ],
    "Level {:d} Golem Mastery Aura When Equipped": [
        "151,79"
    ],
    "Level {:d} Raise Skeletal Mage Aura When Equipped": [
        "151,80"
    ],
    "Level {:d} Confuse Aura When Equipped": [
        "151,81"
    ],
    "Level {:d} Life Tap Aura When Equipped": [
        "151,82"
    ],
    "Level {:d} Poison Explosion Aura When Equipped": [
        "151,83"
    ],
    "Level {:d} Bone Spear Aura When Equipped": [
        "151,84"
    ],
    "Level {:d} Blood Golem Aura When Equipped": [
        "151,85"
    ],
    "Level {:d} Attract Aura When Equipped": [
        "151,86"
    ],
    "Level {:d} Decrepify Aura When Equipped": [
        "151,87"
    ],
    "Level {:d} Bone Prison Aura When Equipped": [
        "151,88"
    ],
    "Level {:d} Summon Resist Aura When Equipped": [
        "151,89"
    ],
    "Level {:d} Iron Golem Aura When Equipped": [
        "151,90"
    ],
    "Level {:d} Lower Resist Aura When Equipped": [
        "151,91"
    ],
    "Level {:d} Poison Nova Aura When Equipped": [
        "151,92"
    ],
    "Level {:d} Bone Spirit Aura When Equipped": [
        "151,93"
    ],
    "Level {:d} Fire Golem Aura When Equipped": [
        "151,94"
    ],
    "Level {:d} Revive Aura When Equipped": [
        "151,95"
    ],
    "Level {:d} Sacrifice Aura When Equipped": [
        "151,96"
    ],
    "Level {:d} Smite Aura When Equipped": [
        "151,97"
    ],
    "Level {:d} Might Aura When Equipped": [
        "151,98"
    ],
    "Level {:d} Prayer Aura When Equipped": [
        "151,99"
    ],
    "Level {:d} Resist Fire Aura When Equipped": [
        "151,100"
    ],
    "Level {:d} Holy Bolt Aura When Equipped": [
        "151,101"
    ],
    "Level {:d} Holy Fire Aura When Equipped": [
        "151,102"
    ],
    "Level {:d} Thorns Aura When Equipped": [
        "151,103"
    ],
    "Level {:d} Defiance Aura When Equipped": [
        "151,104"
    ],
    "Level {:d} Resist Cold Aura When Equipped": [
        "151,105"
    ],
    "Level {:d} Zeal Aura When Equipped": [
        "151,106"
    ],
    "Level {:d} Charge Aura When Equipped": [
        "151,107"
    ],
    "Level {:d} Blessed Aim Aura When Equipped": [
        "151,108"
    ],
    "Level {:d} Cleansing Aura When Equipped": [
        "151,109"
    ],
    "Level {:d} Resist Lightning Aura When Equipped": [
        "151,110"
    ],
    "Level {:d} Vengeance Aura When Equipped": [
        "151,111"
    ],
    "Level {:d} Blessed Hammer Aura When Equipped": [
        "151,112"
    ],
    "Level {:d} Concentration Aura When Equipped": [
        "151,113"
    ],
    "Level {:d} Holy Freeze Aura When Equipped": [
        "151,114"
    ],
    "Level {:d} Vigor Aura When Equipped": [
        "151,115"
    ],
    "Level {:d} Conversion Aura When Equipped": [
        "151,116"
    ],
    "Level {:d} Holy Shield Aura When Equipped": [
        "151,117"
    ],
    "Level {:d} Holy Shock Aura When Equipped": [
        "151,118"
    ],
    "Level {:d} Sanctuary Aura When Equipped": [
        "151,119"
    ],
    "Level {:d} Meditation Aura When Equipped": [
        "151,120"
    ],
    "Level {:d} Fist of the Heavens Aura When Equipped": [
        "151,121"
    ],
    "Level {:d} Fanaticism Aura When Equipped": [
        "151,122"
    ],
    "Level {:d} Conviction Aura When Equipped": [
        "151,123"
    ],
    "Level {:d} Redemption Aura When Equipped": [
        "151,124"
    ],
    "Level {:d} Salvation Aura When Equipped": [
        "151,125"
    ],
    "Level {:d} Bash Aura When Equipped": [
        "151,126"
    ],
    "Level {:d} Blade Mastery Aura When Equipped": [
        "151,127"
    ],
    "Level {:d} Axe Mastery Aura When Equipped": [
        "151,128"
    ],
    "Level {:d} Mace Mastery Aura When Equipped": [
        "151,129"
    ],
    "Level {:d} Howl Aura When Equipped": [
        "151,130"
    ],
    "Level {:d} Find Potion Aura When Equipped": [
        "151,131"
    ],
    "Level {:d} Leap Aura When Equipped": [
        "151,132"
    ],
    "Level {:d} Double Swing Aura When Equipped": [
        "151,133"
    ],
    "Level {:d} Polearm Mastery Aura When Equipped": [
        "151,134"
    ],
    "Level {:d} Throwing Mastery Aura When Equipped": [
        "151,135"
    ],
    "Level {:d} Spear Mastery Aura When Equipped": [
        "151,136"
    ],
    "Level {:d} Taunt Aura When Equipped": [
        "151,137"
    ],
    "Level {:d} Shout Aura When Equipped": [
        "151,138"
    ],
    "Level {:d} Stun Aura When Equipped": [
        "151,139"
    ],
    "Level {:d} Double Throw Aura When Equipped": [
        "151,140"
    ],
    "Level {:d} Increased Stamina Aura When Equipped": [
        "151,141"
    ],
    "Level {:d} Find Item Aura When Equipped": [
        "151,142"
    ],
    "Level {:d} Leap Attack Aura When Equipped": [
        "151,143"
    ],
    "Level {:d} Concentrate Aura When Equipped": [
        "151,144"
    ],
    "Level {:d} Iron Skin Aura When Equipped": [
        "151,145"
    ],
    "Level {:d} Battle Cry Aura When Equipped": [
        "151,146"
    ],
    "Level {:d} Frenzy Aura When Equipped": [
        "151,147"
    ],
    "Level {:d} Increased Speed Aura When Equipped": [
        "151,148"
    ],
    "Level {:d} Battle Orders Aura When Equipped": [
        "151,149"
    ],
    "Level {:d} Grim Ward Aura When Equipped": [
        "151,150"
    ],
    "Level {:d} Whirlwind Aura When Equipped": [
        "151,151"
    ],
    "Level {:d} Berserk Aura When Equipped": [
        "151,152"
    ],
    "Level {:d} Natural Resistance Aura When Equipped": [
        "151,153"
    ],
    "Level {:d} War Cry Aura When Equipped": [
        "151,154"
    ],
    "Level {:d} Battle Command Aura When Equipped": [
        "151,155"
    ],
    "Level {:d} Raven Aura When Equipped": [
        "151,221"
    ],
    "Level {:d} Poison Creeper Aura When Equipped": [
        "151,222"
    ],
    "Level {:d} Werewolf Aura When Equipped": [
        "151,223"
    ],
    "Level {:d} Lycanthropy Aura When Equipped": [
        "151,224"
    ],
    "Level {:d} Firestorm Aura When Equipped": [
        "151,225"
    ],
    "Level {:d} Oak Sage Aura When Equipped": [
        "151,226"
    ],
    "Level {:d} Summon Spirit Wolf Aura When Equipped": [
        "151,227"
    ],
    "Level {:d} Werebear Aura When Equipped": [
        "151,228"
    ],
    "Level {:d} Molten Boulder Aura When Equipped": [
        "151,229"
    ],
    "Level {:d} Arctic Blast Aura When Equipped": [
        "151,230"
    ],
    "Level {:d} Carrion Vine Aura When Equipped": [
        "151,231"
    ],
    "Level {:d} Feral Rage Aura When Equipped": [
        "151,232"
    ],
    "Level {:d} Maul Aura When Equipped": [
        "151,233"
    ],
    "Level {:d} Fissure Aura When Equipped": [
        "151,234"
    ],
    "Level {:d} Cyclone Armor Aura When Equipped": [
        "151,235"
    ],
    "Level {:d} Heart of Wolverine Aura When Equipped": [
        "151,236"
    ],
    "Level {:d} Summon Dire Wolf Aura When Equipped": [
        "151,237"
    ],
    "Level {:d} Rabies Aura When Equipped": [
        "151,238"
    ],
    "Level {:d} Fire Claws Aura When Equipped": [
        "151,239"
    ],
    "Level {:d} Twister Aura When Equipped": [
        "151,240"
    ],
    "Level {:d} Solar Creeper Aura When Equipped": [
        "151,241"
    ],
    "Level {:d} Hunger Aura When Equipped": [
        "151,242"
    ],
    "Level {:d} Shock Wave Aura When Equipped": [
        "151,243"
    ],
    "Level {:d} Volcano Aura When Equipped": [
        "151,244"
    ],
    "Level {:d} Tornado Aura When Equipped": [
        "151,245"
    ],
    "Level {:d} Spirit of Barbs Aura When Equipped": [
        "151,246"
    ],
    "Level {:d} Summon Grizzly Aura When Equipped": [
        "151,247"
    ],
    "Level {:d} Fury Aura When Equipped": [
        "151,248"
    ],
    "Level {:d} Armageddon Aura When Equipped": [
        "151,249"
    ],
    "Level {:d} Hurricane Aura When Equipped": [
        "151,250"
    ],
    "Level {:d} Fire Blast Aura When Equipped": [
        "151,251"
    ],
    "Level {:d} Claw Mastery Aura When Equipped": [
        "151,252"
    ],
    "Level {:d} Psychic Hammer Aura When Equipped": [
        "151,253"
    ],
    "Level {:d} Tiger Strike Aura When Equipped": [
        "151,254"
    ],
    "Level {:d} Dragon Talon Aura When Equipped": [
        "151,255"
    ],
    "Level {:d} Shock Web Aura When Equipped": [
        "151,256"
    ],
    "Level {:d} Blade Sentinel Aura When Equipped": [
        "151,257"
    ],
    "Level {:d} Burst of Speed Aura When Equipped": [
        "151,258"
    ],
    "Level {:d} Fists of Fire Aura When Equipped": [
        "151,259"
    ],
    "Level {:d} Dragon Claw Aura When Equipped": [
        "151,260"
    ],
    "Level {:d} Charged Bolt Sentry Aura When Equipped": [
        "151,261"
    ],
    "Level {:d} Wake of Fire Aura When Equipped": [
        "151,262"
    ],
    "Level {:d} Weapon Block Aura When Equipped": [
        "151,263"
    ],
    "Level {:d} Cloak of Shadows Aura When Equipped": [
        "151,264"
    ],
    "Level {:d} Cobra Strike Aura When Equipped": [
        "151,265"
    ],
    "Level {:d} Blade Fury Aura When Equipped": [
        "151,266"
    ],
    "Level {:d} Fade Aura When Equipped": [
        "151,267"
    ],
    "Level {:d} Shadow Warrior Aura When Equipped": [
        "151,268"
    ],
    "Level {:d} Claws of Thunder Aura When Equipped": [
        "151,269"
    ],
    "Level {:d} Dragon Tail Aura When Equipped": [
        "151,270"
    ],
    "Level {:d} Lightning Sentry Aura When Equipped": [
        "151,271"
    ],
    "Level {:d} Wake of Inferno Aura When Equipped": [
        "151,272"
    ],
    "Level {:d} Mind Blast Aura When Equipped": [
        "151,273"
    ],
    "Level {:d} Blades of Ice Aura When Equipped": [
        "151,274"
    ],
    "Level {:d} Dragon Flight Aura When Equipped": [
        "151,275"
    ],
    "Level {:d} Death Sentry Aura When Equipped": [
        "151,276"
    ],
    "Level {:d} Blade Shield Aura When Equipped": [
        "151,277"
    ],
    "Level {:d} Venom Aura When Equipped": [
        "151,278"
    ],
    "Level {:d} Shadow Master Aura When Equipped": [
        "151,279"
    ],
    "Level {:d} Phoenix Strike Aura When Equipped": [
        "151,280"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow on attack": [
        "195,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow on attack": [
        "195,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight on attack": [
        "195,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike on attack": [
        "195,9"
    ],
    "{:d}% Chance to cast level {:d} Jab on attack": [
        "195,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow on attack": [
        "195,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot on attack": [
        "195,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge on attack": [
        "195,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike on attack": [
        "195,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin on attack": [
        "195,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow on attack": [
        "195,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles on attack": [
        "195,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid on attack": [
        "195,18"
    ],
    "{:d}% Chance to cast level {:d} Impale on attack": [
        "195,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt on attack": [
        "195,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow on attack": [
        "195,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow on attack": [
        "195,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate on attack": [
        "195,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike on attack": [
        "195,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin on attack": [
        "195,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe on attack": [
        "195,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow on attack": [
        "195,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy on attack": [
        "195,28"
    ],
    "{:d}% Chance to cast level {:d} Evade on attack": [
        "195,29"
    ],
    "{:d}% Chance to cast level {:d} Fend on attack": [
        "195,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow on attack": [
        "195,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie on attack": [
        "195,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce on attack": [
        "195,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike on attack": [
        "195,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury on attack": [
        "195,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt on attack": [
        "195,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth on attack": [
        "195,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt on attack": [
        "195,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt on attack": [
        "195,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor on attack": [
        "195,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno on attack": [
        "195,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field on attack": [
        "195,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis on attack": [
        "195,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova on attack": [
        "195,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast on attack": [
        "195,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze on attack": [
        "195,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball on attack": [
        "195,47"
    ],
    "{:d}% Chance to cast level {:d} Nova on attack": [
        "195,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning on attack": [
        "195,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor on attack": [
        "195,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall on attack": [
        "195,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant on attack": [
        "195,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning on attack": [
        "195,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport on attack": [
        "195,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike on attack": [
        "195,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor on attack": [
        "195,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm on attack": [
        "195,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield on attack": [
        "195,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard on attack": [
        "195,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor on attack": [
        "195,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery on attack": [
        "195,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra on attack": [
        "195,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery on attack": [
        "195,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb on attack": [
        "195,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery on attack": [
        "195,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage on attack": [
        "195,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth on attack": [
        "195,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor on attack": [
        "195,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery on attack": [
        "195,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton on attack": [
        "195,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision on attack": [
        "195,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken on attack": [
        "195,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger on attack": [
        "195,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion on attack": [
        "195,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem on attack": [
        "195,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden on attack": [
        "195,76"
    ],
    "{:d}% Chance to cast level {:d} Terror on attack": [
        "195,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall on attack": [
        "195,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery on attack": [
        "195,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage on attack": [
        "195,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse on attack": [
        "195,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap on attack": [
        "195,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion on attack": [
        "195,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear on attack": [
        "195,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem on attack": [
        "195,85"
    ],
    "{:d}% Chance to cast level {:d} Attract on attack": [
        "195,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify on attack": [
        "195,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison on attack": [
        "195,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist on attack": [
        "195,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem on attack": [
        "195,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist on attack": [
        "195,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova on attack": [
        "195,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit on attack": [
        "195,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem on attack": [
        "195,94"
    ],
    "{:d}% Chance to cast level {:d} Revive on attack": [
        "195,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice on attack": [
        "195,96"
    ],
    "{:d}% Chance to cast level {:d} Smite on attack": [
        "195,97"
    ],
    "{:d}% Chance to cast level {:d} Might on attack": [
        "195,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer on attack": [
        "195,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire on attack": [
        "195,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt on attack": [
        "195,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire on attack": [
        "195,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns on attack": [
        "195,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance on attack": [
        "195,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold on attack": [
        "195,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal on attack": [
        "195,106"
    ],
    "{:d}% Chance to cast level {:d} Charge on attack": [
        "195,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim on attack": [
        "195,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing on attack": [
        "195,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning on attack": [
        "195,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance on attack": [
        "195,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer on attack": [
        "195,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration on attack": [
        "195,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze on attack": [
        "195,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor on attack": [
        "195,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion on attack": [
        "195,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield on attack": [
        "195,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock on attack": [
        "195,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary on attack": [
        "195,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation on attack": [
        "195,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens on attack": [
        "195,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism on attack": [
        "195,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction on attack": [
        "195,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption on attack": [
        "195,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation on attack": [
        "195,125"
    ],
    "{:d}% Chance to cast level {:d} Bash on attack": [
        "195,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery on attack": [
        "195,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery on attack": [
        "195,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery on attack": [
        "195,129"
    ],
    "{:d}% Chance to cast level {:d} Howl on attack": [
        "195,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion on attack": [
        "195,131"
    ],
    "{:d}% Chance to cast level {:d} Leap on attack": [
        "195,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing on attack": [
        "195,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery on attack": [
        "195,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery on attack": [
        "195,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery on attack": [
        "195,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt on attack": [
        "195,137"
    ],
    "{:d}% Chance to cast level {:d} Shout on attack": [
        "195,138"
    ],
    "{:d}% Chance to cast level {:d} Stun on attack": [
        "195,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw on attack": [
        "195,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina on attack": [
        "195,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item on attack": [
        "195,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack on attack": [
        "195,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate on attack": [
        "195,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin on attack": [
        "195,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry on attack": [
        "195,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy on attack": [
        "195,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed on attack": [
        "195,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders on attack": [
        "195,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward on attack": [
        "195,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind on attack": [
        "195,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk on attack": [
        "195,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance on attack": [
        "195,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry on attack": [
        "195,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command on attack": [
        "195,155"
    ],
    "{:d}% Chance to cast level {:d} Raven on attack": [
        "195,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper on attack": [
        "195,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf on attack": [
        "195,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy on attack": [
        "195,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm on attack": [
        "195,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage on attack": [
        "195,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf on attack": [
        "195,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear on attack": [
        "195,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder on attack": [
        "195,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast on attack": [
        "195,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine on attack": [
        "195,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage on attack": [
        "195,232"
    ],
    "{:d}% Chance to cast level {:d} Maul on attack": [
        "195,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure on attack": [
        "195,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor on attack": [
        "195,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine on attack": [
        "195,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf on attack": [
        "195,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies on attack": [
        "195,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws on attack": [
        "195,239"
    ],
    "{:d}% Chance to cast level {:d} Twister on attack": [
        "195,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper on attack": [
        "195,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger on attack": [
        "195,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave on attack": [
        "195,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano on attack": [
        "195,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado on attack": [
        "195,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs on attack": [
        "195,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly on attack": [
        "195,247"
    ],
    "{:d}% Chance to cast level {:d} Fury on attack": [
        "195,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon on attack": [
        "195,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane on attack": [
        "195,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast on attack": [
        "195,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery on attack": [
        "195,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer on attack": [
        "195,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike on attack": [
        "195,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon on attack": [
        "195,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web on attack": [
        "195,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel on attack": [
        "195,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed on attack": [
        "195,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire on attack": [
        "195,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw on attack": [
        "195,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry on attack": [
        "195,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire on attack": [
        "195,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block on attack": [
        "195,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows on attack": [
        "195,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike on attack": [
        "195,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury on attack": [
        "195,266"
    ],
    "{:d}% Chance to cast level {:d} Fade on attack": [
        "195,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior on attack": [
        "195,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder on attack": [
        "195,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail on attack": [
        "195,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry on attack": [
        "195,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno on attack": [
        "195,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast on attack": [
        "195,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice on attack": [
        "195,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight on attack": [
        "195,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry on attack": [
        "195,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield on attack": [
        "195,277"
    ],
    "{:d}% Chance to cast level {:d} Venom on attack": [
        "195,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master on attack": [
        "195,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike on attack": [
        "195,280"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow on striking": [
        "198,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow on striking": [
        "198,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight on striking": [
        "198,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike on striking": [
        "198,9"
    ],
    "{:d}% Chance to cast level {:d} Jab on striking": [
        "198,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow on striking": [
        "198,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot on striking": [
        "198,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge on striking": [
        "198,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike on striking": [
        "198,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin on striking": [
        "198,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow on striking": [
        "198,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles on striking": [
        "198,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid on striking": [
        "198,18"
    ],
    "{:d}% Chance to cast level {:d} Impale on striking": [
        "198,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt on striking": [
        "198,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow on striking": [
        "198,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow on striking": [
        "198,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate on striking": [
        "198,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike on striking": [
        "198,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin on striking": [
        "198,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe on striking": [
        "198,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow on striking": [
        "198,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy on striking": [
        "198,28"
    ],
    "{:d}% Chance to cast level {:d} Evade on striking": [
        "198,29"
    ],
    "{:d}% Chance to cast level {:d} Fend on striking": [
        "198,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow on striking": [
        "198,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie on striking": [
        "198,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce on striking": [
        "198,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike on striking": [
        "198,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury on striking": [
        "198,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt on striking": [
        "198,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth on striking": [
        "198,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt on striking": [
        "198,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt on striking": [
        "198,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor on striking": [
        "198,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno on striking": [
        "198,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field on striking": [
        "198,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis on striking": [
        "198,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova on striking": [
        "198,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast on striking": [
        "198,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze on striking": [
        "198,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball on striking": [
        "198,47"
    ],
    "{:d}% Chance to cast level {:d} Nova on striking": [
        "198,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning on striking": [
        "198,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor on striking": [
        "198,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall on striking": [
        "198,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant on striking": [
        "198,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning on striking": [
        "198,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport on striking": [
        "198,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike on striking": [
        "198,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor on striking": [
        "198,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm on striking": [
        "198,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield on striking": [
        "198,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard on striking": [
        "198,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor on striking": [
        "198,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery on striking": [
        "198,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra on striking": [
        "198,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery on striking": [
        "198,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb on striking": [
        "198,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery on striking": [
        "198,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage on striking": [
        "198,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth on striking": [
        "198,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor on striking": [
        "198,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery on striking": [
        "198,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton on striking": [
        "198,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision on striking": [
        "198,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken on striking": [
        "198,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger on striking": [
        "198,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion on striking": [
        "198,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem on striking": [
        "198,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden on striking": [
        "198,76"
    ],
    "{:d}% Chance to cast level {:d} Terror on striking": [
        "198,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall on striking": [
        "198,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery on striking": [
        "198,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage on striking": [
        "198,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse on striking": [
        "198,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap on striking": [
        "198,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion on striking": [
        "198,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear on striking": [
        "198,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem on striking": [
        "198,85"
    ],
    "{:d}% Chance to cast level {:d} Attract on striking": [
        "198,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify on striking": [
        "198,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison on striking": [
        "198,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist on striking": [
        "198,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem on striking": [
        "198,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist on striking": [
        "198,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova on striking": [
        "198,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit on striking": [
        "198,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem on striking": [
        "198,94"
    ],
    "{:d}% Chance to cast level {:d} Revive on striking": [
        "198,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice on striking": [
        "198,96"
    ],
    "{:d}% Chance to cast level {:d} Smite on striking": [
        "198,97"
    ],
    "{:d}% Chance to cast level {:d} Might on striking": [
        "198,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer on striking": [
        "198,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire on striking": [
        "198,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt on striking": [
        "198,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire on striking": [
        "198,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns on striking": [
        "198,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance on striking": [
        "198,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold on striking": [
        "198,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal on striking": [
        "198,106"
    ],
    "{:d}% Chance to cast level {:d} Charge on striking": [
        "198,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim on striking": [
        "198,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing on striking": [
        "198,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning on striking": [
        "198,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance on striking": [
        "198,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer on striking": [
        "198,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration on striking": [
        "198,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze on striking": [
        "198,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor on striking": [
        "198,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion on striking": [
        "198,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield on striking": [
        "198,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock on striking": [
        "198,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary on striking": [
        "198,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation on striking": [
        "198,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens on striking": [
        "198,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism on striking": [
        "198,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction on striking": [
        "198,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption on striking": [
        "198,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation on striking": [
        "198,125"
    ],
    "{:d}% Chance to cast level {:d} Bash on striking": [
        "198,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery on striking": [
        "198,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery on striking": [
        "198,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery on striking": [
        "198,129"
    ],
    "{:d}% Chance to cast level {:d} Howl on striking": [
        "198,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion on striking": [
        "198,131"
    ],
    "{:d}% Chance to cast level {:d} Leap on striking": [
        "198,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing on striking": [
        "198,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery on striking": [
        "198,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery on striking": [
        "198,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery on striking": [
        "198,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt on striking": [
        "198,137"
    ],
    "{:d}% Chance to cast level {:d} Shout on striking": [
        "198,138"
    ],
    "{:d}% Chance to cast level {:d} Stun on striking": [
        "198,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw on striking": [
        "198,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina on striking": [
        "198,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item on striking": [
        "198,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack on striking": [
        "198,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate on striking": [
        "198,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin on striking": [
        "198,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry on striking": [
        "198,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy on striking": [
        "198,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed on striking": [
        "198,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders on striking": [
        "198,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward on striking": [
        "198,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind on striking": [
        "198,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk on striking": [
        "198,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance on striking": [
        "198,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry on striking": [
        "198,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command on striking": [
        "198,155"
    ],
    "{:d}% Chance to cast level {:d} Raven on striking": [
        "198,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper on striking": [
        "198,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf on striking": [
        "198,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy on striking": [
        "198,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm on striking": [
        "198,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage on striking": [
        "198,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf on striking": [
        "198,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear on striking": [
        "198,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder on striking": [
        "198,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast on striking": [
        "198,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine on striking": [
        "198,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage on striking": [
        "198,232"
    ],
    "{:d}% Chance to cast level {:d} Maul on striking": [
        "198,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure on striking": [
        "198,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor on striking": [
        "198,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine on striking": [
        "198,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf on striking": [
        "198,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies on striking": [
        "198,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws on striking": [
        "198,239"
    ],
    "{:d}% Chance to cast level {:d} Twister on striking": [
        "198,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper on striking": [
        "198,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger on striking": [
        "198,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave on striking": [
        "198,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano on striking": [
        "198,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado on striking": [
        "198,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs on striking": [
        "198,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly on striking": [
        "198,247"
    ],
    "{:d}% Chance to cast level {:d} Fury on striking": [
        "198,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon on striking": [
        "198,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane on striking": [
        "198,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast on striking": [
        "198,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery on striking": [
        "198,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer on striking": [
        "198,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike on striking": [
        "198,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon on striking": [
        "198,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web on striking": [
        "198,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel on striking": [
        "198,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed on striking": [
        "198,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire on striking": [
        "198,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw on striking": [
        "198,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry on striking": [
        "198,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire on striking": [
        "198,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block on striking": [
        "198,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows on striking": [
        "198,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike on striking": [
        "198,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury on striking": [
        "198,266"
    ],
    "{:d}% Chance to cast level {:d} Fade on striking": [
        "198,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior on striking": [
        "198,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder on striking": [
        "198,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail on striking": [
        "198,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry on striking": [
        "198,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno on striking": [
        "198,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast on striking": [
        "198,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice on striking": [
        "198,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight on striking": [
        "198,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry on striking": [
        "198,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield on striking": [
        "198,277"
    ],
    "{:d}% Chance to cast level {:d} Venom on striking": [
        "198,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master on striking": [
        "198,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike on striking": [
        "198,280"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow when struck": [
        "201,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow when struck": [
        "201,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight when struck": [
        "201,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike when struck": [
        "201,9"
    ],
    "{:d}% Chance to cast level {:d} Jab when struck": [
        "201,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow when struck": [
        "201,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot when struck": [
        "201,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge when struck": [
        "201,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike when struck": [
        "201,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin when struck": [
        "201,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow when struck": [
        "201,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles when struck": [
        "201,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid when struck": [
        "201,18"
    ],
    "{:d}% Chance to cast level {:d} Impale when struck": [
        "201,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt when struck": [
        "201,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow when struck": [
        "201,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow when struck": [
        "201,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate when struck": [
        "201,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike when struck": [
        "201,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin when struck": [
        "201,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe when struck": [
        "201,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow when struck": [
        "201,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy when struck": [
        "201,28"
    ],
    "{:d}% Chance to cast level {:d} Evade when struck": [
        "201,29"
    ],
    "{:d}% Chance to cast level {:d} Fend when struck": [
        "201,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow when struck": [
        "201,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie when struck": [
        "201,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce when struck": [
        "201,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike when struck": [
        "201,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury when struck": [
        "201,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt when struck": [
        "201,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth when struck": [
        "201,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt when struck": [
        "201,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt when struck": [
        "201,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor when struck": [
        "201,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno when struck": [
        "201,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field when struck": [
        "201,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis when struck": [
        "201,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova when struck": [
        "201,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast when struck": [
        "201,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze when struck": [
        "201,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball when struck": [
        "201,47"
    ],
    "{:d}% Chance to cast level {:d} Nova when struck": [
        "201,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning when struck": [
        "201,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor when struck": [
        "201,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall when struck": [
        "201,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant when struck": [
        "201,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning when struck": [
        "201,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport when struck": [
        "201,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike when struck": [
        "201,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor when struck": [
        "201,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm when struck": [
        "201,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield when struck": [
        "201,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard when struck": [
        "201,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor when struck": [
        "201,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery when struck": [
        "201,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra when struck": [
        "201,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery when struck": [
        "201,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb when struck": [
        "201,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery when struck": [
        "201,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage when struck": [
        "201,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth when struck": [
        "201,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor when struck": [
        "201,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery when struck": [
        "201,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton when struck": [
        "201,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision when struck": [
        "201,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken when struck": [
        "201,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger when struck": [
        "201,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion when struck": [
        "201,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem when struck": [
        "201,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden when struck": [
        "201,76"
    ],
    "{:d}% Chance to cast level {:d} Terror when struck": [
        "201,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall when struck": [
        "201,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery when struck": [
        "201,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage when struck": [
        "201,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse when struck": [
        "201,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap when struck": [
        "201,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion when struck": [
        "201,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear when struck": [
        "201,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem when struck": [
        "201,85"
    ],
    "{:d}% Chance to cast level {:d} Attract when struck": [
        "201,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify when struck": [
        "201,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison when struck": [
        "201,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist when struck": [
        "201,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem when struck": [
        "201,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist when struck": [
        "201,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova when struck": [
        "201,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit when struck": [
        "201,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem when struck": [
        "201,94"
    ],
    "{:d}% Chance to cast level {:d} Revive when struck": [
        "201,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice when struck": [
        "201,96"
    ],
    "{:d}% Chance to cast level {:d} Smite when struck": [
        "201,97"
    ],
    "{:d}% Chance to cast level {:d} Might when struck": [
        "201,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer when struck": [
        "201,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire when struck": [
        "201,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt when struck": [
        "201,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire when struck": [
        "201,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns when struck": [
        "201,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance when struck": [
        "201,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold when struck": [
        "201,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal when struck": [
        "201,106"
    ],
    "{:d}% Chance to cast level {:d} Charge when struck": [
        "201,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim when struck": [
        "201,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing when struck": [
        "201,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning when struck": [
        "201,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance when struck": [
        "201,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer when struck": [
        "201,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration when struck": [
        "201,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze when struck": [
        "201,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor when struck": [
        "201,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion when struck": [
        "201,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield when struck": [
        "201,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock when struck": [
        "201,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary when struck": [
        "201,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation when struck": [
        "201,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens when struck": [
        "201,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism when struck": [
        "201,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction when struck": [
        "201,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption when struck": [
        "201,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation when struck": [
        "201,125"
    ],
    "{:d}% Chance to cast level {:d} Bash when struck": [
        "201,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery when struck": [
        "201,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery when struck": [
        "201,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery when struck": [
        "201,129"
    ],
    "{:d}% Chance to cast level {:d} Howl when struck": [
        "201,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion when struck": [
        "201,131"
    ],
    "{:d}% Chance to cast level {:d} Leap when struck": [
        "201,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing when struck": [
        "201,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery when struck": [
        "201,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery when struck": [
        "201,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery when struck": [
        "201,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt when struck": [
        "201,137"
    ],
    "{:d}% Chance to cast level {:d} Shout when struck": [
        "201,138"
    ],
    "{:d}% Chance to cast level {:d} Stun when struck": [
        "201,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw when struck": [
        "201,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina when struck": [
        "201,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item when struck": [
        "201,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack when struck": [
        "201,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate when struck": [
        "201,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin when struck": [
        "201,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry when struck": [
        "201,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy when struck": [
        "201,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed when struck": [
        "201,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders when struck": [
        "201,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward when struck": [
        "201,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind when struck": [
        "201,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk when struck": [
        "201,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance when struck": [
        "201,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry when struck": [
        "201,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command when struck": [
        "201,155"
    ],
    "{:d}% Chance to cast level {:d} Raven when struck": [
        "201,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper when struck": [
        "201,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf when struck": [
        "201,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy when struck": [
        "201,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm when struck": [
        "201,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage when struck": [
        "201,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf when struck": [
        "201,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear when struck": [
        "201,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder when struck": [
        "201,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast when struck": [
        "201,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine when struck": [
        "201,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage when struck": [
        "201,232"
    ],
    "{:d}% Chance to cast level {:d} Maul when struck": [
        "201,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure when struck": [
        "201,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor when struck": [
        "201,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine when struck": [
        "201,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf when struck": [
        "201,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies when struck": [
        "201,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws when struck": [
        "201,239"
    ],
    "{:d}% Chance to cast level {:d} Twister when struck": [
        "201,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper when struck": [
        "201,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger when struck": [
        "201,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave when struck": [
        "201,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano when struck": [
        "201,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado when struck": [
        "201,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs when struck": [
        "201,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly when struck": [
        "201,247"
    ],
    "{:d}% Chance to cast level {:d} Fury when struck": [
        "201,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon when struck": [
        "201,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane when struck": [
        "201,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast when struck": [
        "201,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery when struck": [
        "201,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer when struck": [
        "201,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike when struck": [
        "201,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon when struck": [
        "201,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web when struck": [
        "201,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel when struck": [
        "201,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed when struck": [
        "201,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire when struck": [
        "201,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw when struck": [
        "201,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry when struck": [
        "201,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire when struck": [
        "201,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block when struck": [
        "201,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows when struck": [
        "201,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike when struck": [
        "201,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury when struck": [
        "201,266"
    ],
    "{:d}% Chance to cast level {:d} Fade when struck": [
        "201,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior when struck": [
        "201,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder when struck": [
        "201,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail when struck": [
        "201,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry when struck": [
        "201,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno when struck": [
        "201,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast when struck": [
        "201,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice when struck": [
        "201,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight when struck": [
        "201,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry when struck": [
        "201,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield when struck": [
        "201,277"
    ],
    "{:d}% Chance to cast level {:d} Venom when struck": [
        "201,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master when struck": [
        "201,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike when struck": [
        "201,280"
    ],
    "Socketed ({:d})": [
        "194"
    ],
    "Adds {:d}-{:d} Fire Damage": [
        "48",
        "49"
    ],
    "Adds {:d}-{:d} Lightning Damage": [
        "50",
        "51"
    ],
    "Adds {:d}-{:d} Magic Damage": [
        "52",
        "53"
    ],
    "Adds {:d}-{:d} Cold Damage": [
        "54",
        "55"
    ],
    "Adds {:d}-{:d} Poison Damage Over {:d} Seconds": [
        "57",
        "58",
        "59"
    ],
    "Adds {:d}-{:d} Damage": [
        "21",
        "22"
    ],
    "{:d} Defense (Based on Character Level)": [
        "214"
    ],
    "{:d}% Enhanced Defense (Based on Character Level)": [
        "215"
    ],
    "{:d} to Life (Based on Character Level)": [
        "216"
    ],
    "{:d} to Mana (Based on Character Level)": [
        "217"
    ],
    "{:d} to Maximum Damage (Based on Character Level)": [
        "218"
    ],
    "{:d}% Enhanced Maximum Damage (Based on Character Level)": [
        "219"
    ],
    "{:d} to Strength (Based on Character Level)": [
        "220"
    ],
    "{:d} to Dexterity (Based on Character Level)": [
        "221"
    ],
    "{:d} to Vitality (Based on Character Level)": [
        "223"
    ],
    "{:d} to Attack Rating (Based on Character Level)": [
        "224"
    ],
    "{:d}% Bonus to Attack Rating (Based on Character Level)": [
        "225"
    ],
    "Cold Resist {:d}% (Based on Character Level)": [
        "230"
    ],
    "Fire Resist {:d}% (Based on Character Level)": [
        "231"
    ],
    "Lightning Resist {:d}% (Based on Character Level)": [
        "232"
    ],
    "Poison Resist {:d}% (Based on Character Level)": [
        "233"
    ],
    "Absorbs Cold Damage (Based on Character Level)": [
        "234"
    ],
    "Absorbs Fire Damage (Based on Character Level)": [
        "235"
    ],
    "Attacker Takes Damage of {:d} (Based on Character Level)": [
        "238"
    ],
    "{:d}% Extra Gold from Monsters (Based on Character Level)": [
        "239"
    ],
    "{:d}% Better Chance of Getting Magic Items (Based on Character Level)": [
        "240"
    ],
    "Heal Stamina Plus {:d}% (Based on Character Level)": [
        "241"
    ],
    "{:d} Maximum Stamina (Based on Character Level)": [
        "242"
    ],
    "{:d}% Damage to Demons (Based on Character Level)": [
        "243"
    ],
    "{:d}% Damage to Undead (Based on Character Level)": [
        "244"
    ],
    "{:d} to Attack Rating against Demons (Based on Character Level)": [
        "245"
    ],
    "{:d} to Attack Rating against Undead (Based on Character Level)": [
        "246"
    ],
    "{:d}% Deadly Strike (Based on Character Level)": [
        "250"
    ],
    "Repairs 1 durability in {:d} seconds": [
        "252"
    ],
    "Replenishes quantity": [
        "253"
    ],
    "Increased Stack Size": [
        "254"
    ],
    "{:d} Defense (Increases near [Day/Dusk/Night/Dawn])": [
        "268"
    ],
    "{:d}% Enhanced Defense (Increases near [Day/Dusk/Night/Dawn])": [
        "269"
    ],
    "{:d} to Life (Increases near [Day/Dusk/Night/Dawn])": [
        "270"
    ],
    "{:d} to Mana (Increases near [Day/Dusk/Night/Dawn])": [
        "271"
    ],
    "{:d} to Maximum Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "272"
    ],
    "{:d}% Enhanced Maximum Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "273"
    ],
    "{:d} to Strength (Increases near [Day/Dusk/Night/Dawn])": [
        "274"
    ],
    "{:d} to Dexterity (Increases near [Day/Dusk/Night/Dawn])": [
        "275"
    ],
    "{:d} to Energy (Increases near [Day/Dusk/Night/Dawn])": [
        "276"
    ],
    "{:d} to Vitality (Increases near [Day/Dusk/Night/Dawn])": [
        "277"
    ],
    "{:d} to Attack Rating (Increases near [Day/Dusk/Night/Dawn])": [
        "278"
    ],
    "{:d}% Bonus to Attack Rating (Increases near [Day/Dusk/Night/Dawn])": [
        "279"
    ],
    "{:d} to Maximum Cold Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "280"
    ],
    "{:d} to Maximum Fire Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "281"
    ],
    "{:d} to Maximum Lightning Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "282"
    ],
    "{:d} to Maximum Poison Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "283"
    ],
    "Cold Resist {:d}% (Increases near [Day/Dusk/Night/Dawn])": [
        "284"
    ],
    "Fire Resist {:d}% (Increases near [Day/Dusk/Night/Dawn])": [
        "285"
    ],
    "Lightning Resist {:d}% (Increases near [Day/Dusk/Night/Dawn])": [
        "286"
    ],
    "Poison Resist {:d}% (Increases near [Day/Dusk/Night/Dawn])": [
        "287"
    ],
    "Absorbs Cold Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "288"
    ],
    "Absorbs Fire Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "289"
    ],
    "Absorbs Lightning Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "290"
    ],
    "Absorbs Poison Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "291"
    ],
    "{:d}% Extra Gold from Monsters (Increases near [Day/Dusk/Night/Dawn])": [
        "292"
    ],
    "{:d}% Better Chance of Getting Magic Items (Increases near [Day/Dusk/Night/Dawn])": [
        "293"
    ],
    "Heal Stamina Plus {:d}% (Increases near [Day/Dusk/Night/Dawn])": [
        "294"
    ],
    "{:d} Maximum Stamina (Increases near [Day/Dusk/Night/Dawn])": [
        "295"
    ],
    "{:d}% Damage to Demons (Increases near [Day/Dusk/Night/Dawn])": [
        "296"
    ],
    "{:d}% Damage to Undead (Increases near [Day/Dusk/Night/Dawn])": [
        "297"
    ],
    "{:d} to Attack Rating against Demons (Increases near [Day/Dusk/Night/Dawn])": [
        "298"
    ],
    "{:d} to Attack Rating against Undead (Increases near [Day/Dusk/Night/Dawn])": [
        "299"
    ],
    "{:d}% Chance of Crushing Blow (Increases near [Day/Dusk/Night/Dawn])": [
        "300"
    ],
    "{:d}% Chance of Open Wounds (Increases near [Day/Dusk/Night/Dawn])": [
        "301"
    ],
    "{:d} Kick Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "302"
    ],
    "{:d}% Deadly Strike (Increases near [Day/Dusk/Night/Dawn])": [
        "303"
    ],
    "{:d}% to Enemy Fire Resistance": [
        "333"
    ],
    "{:d}% to Enemy Lightning Resistance": [
        "334"
    ],
    "{:d}% to Enemy Cold Resistance": [
        "335"
    ],
    "{:d}% to Enemy Poison Resistance": [
        "336"
    ],
    "Level {:d} Magic Arrow ({:d}/{:d} Charges)": [
        "204,6"
    ],
    "Level {:d} Fire Arrow ({:d}/{:d} Charges)": [
        "204,7"
    ],
    "Level {:d} Inner Sight ({:d}/{:d} Charges)": [
        "204,8"
    ],
    "Level {:d} Critical Strike ({:d}/{:d} Charges)": [
        "204,9"
    ],
    "Level {:d} Jab ({:d}/{:d} Charges)": [
        "204,10"
    ],
    "Level {:d} Cold Arrow ({:d}/{:d} Charges)": [
        "204,11"
    ],
    "Level {:d} Multiple Shot ({:d}/{:d} Charges)": [
        "204,12"
    ],
    "Level {:d} Dodge ({:d}/{:d} Charges)": [
        "204,13"
    ],
    "Level {:d} Power Strike ({:d}/{:d} Charges)": [
        "204,14"
    ],
    "Level {:d} Poison Javelin ({:d}/{:d} Charges)": [
        "204,15"
    ],
    "Level {:d} Exploding Arrow ({:d}/{:d} Charges)": [
        "204,16"
    ],
    "Level {:d} Slow Missiles ({:d}/{:d} Charges)": [
        "204,17"
    ],
    "Level {:d} Avoid ({:d}/{:d} Charges)": [
        "204,18"
    ],
    "Level {:d} Impale ({:d}/{:d} Charges)": [
        "204,19"
    ],
    "Level {:d} Lightning Bolt ({:d}/{:d} Charges)": [
        "204,20"
    ],
    "Level {:d} Ice Arrow ({:d}/{:d} Charges)": [
        "204,21"
    ],
    "Level {:d} Guided Arrow ({:d}/{:d} Charges)": [
        "204,22"
    ],
    "Level {:d} Penetrate ({:d}/{:d} Charges)": [
        "204,23"
    ],
    "Level {:d} Charged Strike ({:d}/{:d} Charges)": [
        "204,24"
    ],
    "Level {:d} Plague Javelin ({:d}/{:d} Charges)": [
        "204,25"
    ],
    "Level {:d} Strafe ({:d}/{:d} Charges)": [
        "204,26"
    ],
    "Level {:d} Immolation Arrow ({:d}/{:d} Charges)": [
        "204,27"
    ],
    "Level {:d} Decoy ({:d}/{:d} Charges)": [
        "204,28"
    ],
    "Level {:d} Evade ({:d}/{:d} Charges)": [
        "204,29"
    ],
    "Level {:d} Fend ({:d}/{:d} Charges)": [
        "204,30"
    ],
    "Level {:d} Freezing Arrow ({:d}/{:d} Charges)": [
        "204,31"
    ],
    "Level {:d} Valkyrie ({:d}/{:d} Charges)": [
        "204,32"
    ],
    "Level {:d} Pierce ({:d}/{:d} Charges)": [
        "204,33"
    ],
    "Level {:d} Lightning Strike ({:d}/{:d} Charges)": [
        "204,34"
    ],
    "Level {:d} Lightning Fury ({:d}/{:d} Charges)": [
        "204,35"
    ],
    "Level {:d} Fire Bolt ({:d}/{:d} Charges)": [
        "204,36"
    ],
    "Level {:d} Warmth ({:d}/{:d} Charges)": [
        "204,37"
    ],
    "Level {:d} Charged Bolt ({:d}/{:d} Charges)": [
        "204,38"
    ],
    "Level {:d} Ice Bolt ({:d}/{:d} Charges)": [
        "204,39"
    ],
    "Level {:d} Frozen Armor ({:d}/{:d} Charges)": [
        "204,40"
    ],
    "Level {:d} Inferno ({:d}/{:d} Charges)": [
        "204,41"
    ],
    "Level {:d} Static Field ({:d}/{:d} Charges)": [
        "204,42"
    ],
    "Level {:d} Telekinesis ({:d}/{:d} Charges)": [
        "204,43"
    ],
    "Level {:d} Frost Nova ({:d}/{:d} Charges)": [
        "204,44"
    ],
    "Level {:d} Ice Blast ({:d}/{:d} Charges)": [
        "204,45"
    ],
    "Level {:d} Blaze ({:d}/{:d} Charges)": [
        "204,46"
    ],
    "Level {:d} Fire Ball ({:d}/{:d} Charges)": [
        "204,47"
    ],
    "Level {:d} Nova ({:d}/{:d} Charges)": [
        "204,48"
    ],
    "Level {:d} Lightning ({:d}/{:d} Charges)": [
        "204,49"
    ],
    "Level {:d} Shiver Armor ({:d}/{:d} Charges)": [
        "204,50"
    ],
    "Level {:d} Fire Wall ({:d}/{:d} Charges)": [
        "204,51"
    ],
    "Level {:d} Enchant ({:d}/{:d} Charges)": [
        "204,52"
    ],
    "Level {:d} Chain Lightning ({:d}/{:d} Charges)": [
        "204,53"
    ],
    "Level {:d} Teleport ({:d}/{:d} Charges)": [
        "204,54"
    ],
    "Level {:d} Glacial Spike ({:d}/{:d} Charges)": [
        "204,55"
    ],
    "Level {:d} Meteor ({:d}/{:d} Charges)": [
        "204,56"
    ],
    "Level {:d} Thunder Storm ({:d}/{:d} Charges)": [
        "204,57"
    ],
    "Level {:d} Energy Shield ({:d}/{:d} Charges)": [
        "204,58"
    ],
    "Level {:d} Blizzard ({:d}/{:d} Charges)": [
        "204,59"
    ],
    "Level {:d} Chilling Armor ({:d}/{:d} Charges)": [
        "204,60"
    ],
    "Level {:d} Fire Mastery ({:d}/{:d} Charges)": [
        "204,61"
    ],
    "Level {:d} Hydra ({:d}/{:d} Charges)": [
        "204,62"
    ],
    "Level {:d} Lightning Mastery ({:d}/{:d} Charges)": [
        "204,63"
    ],
    "Level {:d} Frozen Orb ({:d}/{:d} Charges)": [
        "204,64"
    ],
    "Level {:d} Cold Mastery ({:d}/{:d} Charges)": [
        "204,65"
    ],
    "Level {:d} Amplify Damage ({:d}/{:d} Charges)": [
        "204,66"
    ],
    "Level {:d} Teeth ({:d}/{:d} Charges)": [
        "204,67"
    ],
    "Level {:d} Bone Armor ({:d}/{:d} Charges)": [
        "204,68"
    ],
    "Level {:d} Skeleton Mastery ({:d}/{:d} Charges)": [
        "204,69"
    ],
    "Level {:d} Raise Skeleton ({:d}/{:d} Charges)": [
        "204,70"
    ],
    "Level {:d} Dim Vision ({:d}/{:d} Charges)": [
        "204,71"
    ],
    "Level {:d} Weaken ({:d}/{:d} Charges)": [
        "204,72"
    ],
    "Level {:d} Poison Dagger ({:d}/{:d} Charges)": [
        "204,73"
    ],
    "Level {:d} Corpse Explosion ({:d}/{:d} Charges)": [
        "204,74"
    ],
    "Level {:d} Clay Golem ({:d}/{:d} Charges)": [
        "204,75"
    ],
    "Level {:d} Iron Maiden ({:d}/{:d} Charges)": [
        "204,76"
    ],
    "Level {:d} Terror ({:d}/{:d} Charges)": [
        "204,77"
    ],
    "Level {:d} Bone Wall ({:d}/{:d} Charges)": [
        "204,78"
    ],
    "Level {:d} Golem Mastery ({:d}/{:d} Charges)": [
        "204,79"
    ],
    "Level {:d} Raise Skeletal Mage ({:d}/{:d} Charges)": [
        "204,80"
    ],
    "Level {:d} Confuse ({:d}/{:d} Charges)": [
        "204,81"
    ],
    "Level {:d} Life Tap ({:d}/{:d} Charges)": [
        "204,82"
    ],
    "Level {:d} Poison Explosion ({:d}/{:d} Charges)": [
        "204,83"
    ],
    "Level {:d} Bone Spear ({:d}/{:d} Charges)": [
        "204,84"
    ],
    "Level {:d} Blood Golem ({:d}/{:d} Charges)": [
        "204,85"
    ],
    "Level {:d} Attract ({:d}/{:d} Charges)": [
        "204,86"
    ],
    "Level {:d} Decrepify ({:d}/{:d} Charges)": [
        "204,87"
    ],
    "Level {:d} Bone Prison ({:d}/{:d} Charges)": [
        "204,88"
    ],
    "Level {:d} Summon Resist ({:d}/{:d} Charges)": [
        "204,89"
    ],
    "Level {:d} Iron Golem ({:d}/{:d} Charges)": [
        "204,90"
    ],
    "Level {:d} Lower Resist ({:d}/{:d} Charges)": [
        "204,91"
    ],
    "Level {:d} Poison Nova ({:d}/{:d} Charges)": [
        "204,92"
    ],
    "Level {:d} Bone Spirit ({:d}/{:d} Charges)": [
        "204,93"
    ],
    "Level {:d} Fire Golem ({:d}/{:d} Charges)": [
        "204,94"
    ],
    "Level {:d} Revive ({:d}/{:d} Charges)": [
        "204,95"
    ],
    "Level {:d} Sacrifice ({:d}/{:d} Charges)": [
        "204,96"
    ],
    "Level {:d} Smite ({:d}/{:d} Charges)": [
        "204,97"
    ],
    "Level {:d} Might ({:d}/{:d} Charges)": [
        "204,98"
    ],
    "Level {:d} Prayer ({:d}/{:d} Charges)": [
        "204,99"
    ],
    "Level {:d} Resist Fire ({:d}/{:d} Charges)": [
        "204,100"
    ],
    "Level {:d} Holy Bolt ({:d}/{:d} Charges)": [
        "204,101"
    ],
    "Level {:d} Holy Fire ({:d}/{:d} Charges)": [
        "204,102"
    ],
    "Level {:d} Thorns ({:d}/{:d} Charges)": [
        "204,103"
    ],
    "Level {:d} Defiance ({:d}/{:d} Charges)": [
        "204,104"
    ],
    "Level {:d} Resist Cold ({:d}/{:d} Charges)": [
        "204,105"
    ],
    "Level {:d} Zeal ({:d}/{:d} Charges)": [
        "204,106"
    ],
    "Level {:d} Charge ({:d}/{:d} Charges)": [
        "204,107"
    ],
    "Level {:d} Blessed Aim ({:d}/{:d} Charges)": [
        "204,108"
    ],
    "Level {:d} Cleansing ({:d}/{:d} Charges)": [
        "204,109"
    ],
    "Level {:d} Resist Lightning ({:d}/{:d} Charges)": [
        "204,110"
    ],
    "Level {:d} Vengeance ({:d}/{:d} Charges)": [
        "204,111"
    ],
    "Level {:d} Blessed Hammer ({:d}/{:d} Charges)": [
        "204,112"
    ],
    "Level {:d} Concentration ({:d}/{:d} Charges)": [
        "204,113"
    ],
    "Level {:d} Holy Freeze ({:d}/{:d} Charges)": [
        "204,114"
    ],
    "Level {:d} Vigor ({:d}/{:d} Charges)": [
        "204,115"
    ],
    "Level {:d} Conversion ({:d}/{:d} Charges)": [
        "204,116"
    ],
    "Level {:d} Holy Shield ({:d}/{:d} Charges)": [
        "204,117"
    ],
    "Level {:d} Holy Shock ({:d}/{:d} Charges)": [
        "204,118"
    ],
    "Level {:d} Sanctuary ({:d}/{:d} Charges)": [
        "204,119"
    ],
    "Level {:d} Meditation ({:d}/{:d} Charges)": [
        "204,120"
    ],
    "Level {:d} Fist of the Heavens ({:d}/{:d} Charges)": [
        "204,121"
    ],
    "Level {:d} Fanaticism ({:d}/{:d} Charges)": [
        "204,122"
    ],
    "Level {:d} Conviction ({:d}/{:d} Charges)": [
        "204,123"
    ],
    "Level {:d} Redemption ({:d}/{:d} Charges)": [
        "204,124"
    ],
    "Level {:d} Salvation ({:d}/{:d} Charges)": [
        "204,125"
    ],
    "Level {:d} Bash ({:d}/{:d} Charges)": [
        "204,126"
    ],
    "Level {:d} Blade Mastery ({:d}/{:d} Charges)": [
        "204,127"
    ],
    "Level {:d} Axe Mastery ({:d}/{:d} Charges)": [
        "204,128"
    ],
    "Level {:d} Mace Mastery ({:d}/{:d} Charges)": [
        "204,129"
    ],
    "Level {:d} Howl ({:d}/{:d} Charges)": [
        "204,130"
    ],
    "Level {:d} Find Potion ({:d}/{:d} Charges)": [
        "204,131"
    ],
    "Level {:d} Leap ({:d}/{:d} Charges)": [
        "204,132"
    ],
    "Level {:d} Double Swing ({:d}/{:d} Charges)": [
        "204,133"
    ],
    "Level {:d} Polearm Mastery ({:d}/{:d} Charges)": [
        "204,134"
    ],
    "Level {:d} Throwing Mastery ({:d}/{:d} Charges)": [
        "204,135"
    ],
    "Level {:d} Spear Mastery ({:d}/{:d} Charges)": [
        "204,136"
    ],
    "Level {:d} Taunt ({:d}/{:d} Charges)": [
        "204,137"
    ],
    "Level {:d} Shout ({:d}/{:d} Charges)": [
        "204,138"
    ],
    "Level {:d} Stun ({:d}/{:d} Charges)": [
        "204,139"
    ],
    "Level {:d} Double Throw ({:d}/{:d} Charges)": [
        "204,140"
    ],
    "Level {:d} Increased Stamina ({:d}/{:d} Charges)": [
        "204,141"
    ],
    "Level {:d} Find Item ({:d}/{:d} Charges)": [
        "204,142"
    ],
    "Level {:d} Leap Attack ({:d}/{:d} Charges)": [
        "204,143"
    ],
    "Level {:d} Concentrate ({:d}/{:d} Charges)": [
        "204,144"
    ],
    "Level {:d} Iron Skin ({:d}/{:d} Charges)": [
        "204,145"
    ],
    "Level {:d} Battle Cry ({:d}/{:d} Charges)": [
        "204,146"
    ],
    "Level {:d} Frenzy ({:d}/{:d} Charges)": [
        "204,147"
    ],
    "Level {:d} Increased Speed ({:d}/{:d} Charges)": [
        "204,148"
    ],
    "Level {:d} Battle Orders ({:d}/{:d} Charges)": [
        "204,149"
    ],
    "Level {:d} Grim Ward ({:d}/{:d} Charges)": [
        "204,150"
    ],
    "Level {:d} Whirlwind ({:d}/{:d} Charges)": [
        "204,151"
    ],
    "Level {:d} Berserk ({:d}/{:d} Charges)": [
        "204,152"
    ],
    "Level {:d} Natural Resistance ({:d}/{:d} Charges)": [
        "204,153"
    ],
    "Level {:d} War Cry ({:d}/{:d} Charges)": [
        "204,154"
    ],
    "Level {:d} Battle Command ({:d}/{:d} Charges)": [
        "204,155"
    ],
    "Level {:d} Raven ({:d}/{:d} Charges)": [
        "204,221"
    ],
    "Level {:d} Poison Creeper ({:d}/{:d} Charges)": [
        "204,222"
    ],
    "Level {:d} Werewolf ({:d}/{:d} Charges)": [
        "204,223"
    ],
    "Level {:d} Lycanthropy ({:d}/{:d} Charges)": [
        "204,224"
    ],
    "Level {:d} Firestorm ({:d}/{:d} Charges)": [
        "204,225"
    ],
    "Level {:d} Oak Sage ({:d}/{:d} Charges)": [
        "204,226"
    ],
    "Level {:d} Summon Spirit Wolf ({:d}/{:d} Charges)": [
        "204,227"
    ],
    "Level {:d} Werebear ({:d}/{:d} Charges)": [
        "204,228"
    ],
    "Level {:d} Molten Boulder ({:d}/{:d} Charges)": [
        "204,229"
    ],
    "Level {:d} Arctic Blast ({:d}/{:d} Charges)": [
        "204,230"
    ],
    "Level {:d} Carrion Vine ({:d}/{:d} Charges)": [
        "204,231"
    ],
    "Level {:d} Feral Rage ({:d}/{:d} Charges)": [
        "204,232"
    ],
    "Level {:d} Maul ({:d}/{:d} Charges)": [
        "204,233"
    ],
    "Level {:d} Fissure ({:d}/{:d} Charges)": [
        "204,234"
    ],
    "Level {:d} Cyclone Armor ({:d}/{:d} Charges)": [
        "204,235"
    ],
    "Level {:d} Heart of Wolverine ({:d}/{:d} Charges)": [
        "204,236"
    ],
    "Level {:d} Summon Dire Wolf ({:d}/{:d} Charges)": [
        "204,237"
    ],
    "Level {:d} Rabies ({:d}/{:d} Charges)": [
        "204,238"
    ],
    "Level {:d} Fire Claws ({:d}/{:d} Charges)": [
        "204,239"
    ],
    "Level {:d} Twister ({:d}/{:d} Charges)": [
        "204,240"
    ],
    "Level {:d} Solar Creeper ({:d}/{:d} Charges)": [
        "204,241"
    ],
    "Level {:d} Hunger ({:d}/{:d} Charges)": [
        "204,242"
    ],
    "Level {:d} Shock Wave ({:d}/{:d} Charges)": [
        "204,243"
    ],
    "Level {:d} Volcano ({:d}/{:d} Charges)": [
        "204,244"
    ],
    "Level {:d} Tornado ({:d}/{:d} Charges)": [
        "204,245"
    ],
    "Level {:d} Spirit of Barbs ({:d}/{:d} Charges)": [
        "204,246"
    ],
    "Level {:d} Summon Grizzly ({:d}/{:d} Charges)": [
        "204,247"
    ],
    "Level {:d} Fury ({:d}/{:d} Charges)": [
        "204,248"
    ],
    "Level {:d} Armageddon ({:d}/{:d} Charges)": [
        "204,249"
    ],
    "Level {:d} Hurricane ({:d}/{:d} Charges)": [
        "204,250"
    ],
    "Level {:d} Fire Blast ({:d}/{:d} Charges)": [
        "204,251"
    ],
    "Level {:d} Claw Mastery ({:d}/{:d} Charges)": [
        "204,252"
    ],
    "Level {:d} Psychic Hammer ({:d}/{:d} Charges)": [
        "204,253"
    ],
    "Level {:d} Tiger Strike ({:d}/{:d} Charges)": [
        "204,254"
    ],
    "Level {:d} Dragon Talon ({:d}/{:d} Charges)": [
        "204,255"
    ],
    "Level {:d} Shock Web ({:d}/{:d} Charges)": [
        "204,256"
    ],
    "Level {:d} Blade Sentinel ({:d}/{:d} Charges)": [
        "204,257"
    ],
    "Level {:d} Burst of Speed ({:d}/{:d} Charges)": [
        "204,258"
    ],
    "Level {:d} Fists of Fire ({:d}/{:d} Charges)": [
        "204,259"
    ],
    "Level {:d} Dragon Claw ({:d}/{:d} Charges)": [
        "204,260"
    ],
    "Level {:d} Charged Bolt Sentry ({:d}/{:d} Charges)": [
        "204,261"
    ],
    "Level {:d} Wake of Fire ({:d}/{:d} Charges)": [
        "204,262"
    ],
    "Level {:d} Weapon Block ({:d}/{:d} Charges)": [
        "204,263"
    ],
    "Level {:d} Cloak of Shadows ({:d}/{:d} Charges)": [
        "204,264"
    ],
    "Level {:d} Cobra Strike ({:d}/{:d} Charges)": [
        "204,265"
    ],
    "Level {:d} Blade Fury ({:d}/{:d} Charges)": [
        "204,266"
    ],
    "Level {:d} Fade ({:d}/{:d} Charges)": [
        "204,267"
    ],
    "Level {:d} Shadow Warrior ({:d}/{:d} Charges)": [
        "204,268"
    ],
    "Level {:d} Claws of Thunder ({:d}/{:d} Charges)": [
        "204,269"
    ],
    "Level {:d} Dragon Tail ({:d}/{:d} Charges)": [
        "204,270"
    ],
    "Level {:d} Lightning Sentry ({:d}/{:d} Charges)": [
        "204,271"
    ],
    "Level {:d} Wake of Inferno ({:d}/{:d} Charges)": [
        "204,272"
    ],
    "Level {:d} Mind Blast ({:d}/{:d} Charges)": [
        "204,273"
    ],
    "Level {:d} Blades of Ice ({:d}/{:d} Charges)": [
        "204,274"
    ],
    "Level {:d} Dragon Flight ({:d}/{:d} Charges)": [
        "204,275"
    ],
    "Level {:d} Death Sentry ({:d}/{:d} Charges)": [
        "204,276"
    ],
    "Level {:d} Blade Shield ({:d}/{:d} Charges)": [
        "204,277"
    ],
    "Level {:d} Venom ({:d}/{:d} Charges)": [
        "204,278"
    ],
    "Level {:d} Shadow Master ({:d}/{:d} Charges)": [
        "204,279"
    ],
    "Level {:d} Phoenix Strike ({:d}/{:d} Charges)": [
        "204,280"
    ],
    "{:d}% to Fire Skill Damage": [
        "329"
    ],
    "{:d}% to Lightning Skill Damage": [
        "330"
    ],
    "{:d}% to Cold Skill Damage": [
        "331"
    ],
    "{:d}% to Poison Skill Damage": [
        "332"
    ],
    "Adds {:d}-{:d} Fire/Lightning/Cold Damage": [
        "48",
        "49"
    ],
    "{:d} to all Attributes": [
        [
            "420",
            "0",
            "2",
            "3",
            "1"
        ]
    ],
    "{:d}% to Experience Gained": [
        "85"
    ],
    "{:d} Life after each Kill": [
        "86"
    ],
    "Reduces all Vendor Prices {:d}%": [
        "87"
    ],
    "Slain Monsters Rest in Peace": [
        "108"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow when you Kill an Enemy": [
        "196,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow when you Kill an Enemy": [
        "196,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight when you Kill an Enemy": [
        "196,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike when you Kill an Enemy": [
        "196,9"
    ],
    "{:d}% Chance to cast level {:d} Jab when you Kill an Enemy": [
        "196,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow when you Kill an Enemy": [
        "196,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot when you Kill an Enemy": [
        "196,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge when you Kill an Enemy": [
        "196,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike when you Kill an Enemy": [
        "196,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin when you Kill an Enemy": [
        "196,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow when you Kill an Enemy": [
        "196,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles when you Kill an Enemy": [
        "196,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid when you Kill an Enemy": [
        "196,18"
    ],
    "{:d}% Chance to cast level {:d} Impale when you Kill an Enemy": [
        "196,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt when you Kill an Enemy": [
        "196,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow when you Kill an Enemy": [
        "196,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow when you Kill an Enemy": [
        "196,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate when you Kill an Enemy": [
        "196,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike when you Kill an Enemy": [
        "196,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin when you Kill an Enemy": [
        "196,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe when you Kill an Enemy": [
        "196,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow when you Kill an Enemy": [
        "196,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy when you Kill an Enemy": [
        "196,28"
    ],
    "{:d}% Chance to cast level {:d} Evade when you Kill an Enemy": [
        "196,29"
    ],
    "{:d}% Chance to cast level {:d} Fend when you Kill an Enemy": [
        "196,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow when you Kill an Enemy": [
        "196,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie when you Kill an Enemy": [
        "196,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce when you Kill an Enemy": [
        "196,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike when you Kill an Enemy": [
        "196,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury when you Kill an Enemy": [
        "196,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt when you Kill an Enemy": [
        "196,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth when you Kill an Enemy": [
        "196,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt when you Kill an Enemy": [
        "196,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt when you Kill an Enemy": [
        "196,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor when you Kill an Enemy": [
        "196,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno when you Kill an Enemy": [
        "196,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field when you Kill an Enemy": [
        "196,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis when you Kill an Enemy": [
        "196,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova when you Kill an Enemy": [
        "196,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast when you Kill an Enemy": [
        "196,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze when you Kill an Enemy": [
        "196,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball when you Kill an Enemy": [
        "196,47"
    ],
    "{:d}% Chance to cast level {:d} Nova when you Kill an Enemy": [
        "196,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning when you Kill an Enemy": [
        "196,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor when you Kill an Enemy": [
        "196,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall when you Kill an Enemy": [
        "196,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant when you Kill an Enemy": [
        "196,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning when you Kill an Enemy": [
        "196,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport when you Kill an Enemy": [
        "196,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike when you Kill an Enemy": [
        "196,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor when you Kill an Enemy": [
        "196,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm when you Kill an Enemy": [
        "196,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield when you Kill an Enemy": [
        "196,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard when you Kill an Enemy": [
        "196,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor when you Kill an Enemy": [
        "196,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery when you Kill an Enemy": [
        "196,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra when you Kill an Enemy": [
        "196,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery when you Kill an Enemy": [
        "196,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb when you Kill an Enemy": [
        "196,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery when you Kill an Enemy": [
        "196,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage when you Kill an Enemy": [
        "196,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth when you Kill an Enemy": [
        "196,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor when you Kill an Enemy": [
        "196,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery when you Kill an Enemy": [
        "196,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton when you Kill an Enemy": [
        "196,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision when you Kill an Enemy": [
        "196,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken when you Kill an Enemy": [
        "196,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger when you Kill an Enemy": [
        "196,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion when you Kill an Enemy": [
        "196,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem when you Kill an Enemy": [
        "196,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden when you Kill an Enemy": [
        "196,76"
    ],
    "{:d}% Chance to cast level {:d} Terror when you Kill an Enemy": [
        "196,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall when you Kill an Enemy": [
        "196,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery when you Kill an Enemy": [
        "196,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage when you Kill an Enemy": [
        "196,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse when you Kill an Enemy": [
        "196,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap when you Kill an Enemy": [
        "196,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion when you Kill an Enemy": [
        "196,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear when you Kill an Enemy": [
        "196,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem when you Kill an Enemy": [
        "196,85"
    ],
    "{:d}% Chance to cast level {:d} Attract when you Kill an Enemy": [
        "196,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify when you Kill an Enemy": [
        "196,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison when you Kill an Enemy": [
        "196,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist when you Kill an Enemy": [
        "196,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem when you Kill an Enemy": [
        "196,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist when you Kill an Enemy": [
        "196,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova when you Kill an Enemy": [
        "196,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit when you Kill an Enemy": [
        "196,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem when you Kill an Enemy": [
        "196,94"
    ],
    "{:d}% Chance to cast level {:d} Revive when you Kill an Enemy": [
        "196,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice when you Kill an Enemy": [
        "196,96"
    ],
    "{:d}% Chance to cast level {:d} Smite when you Kill an Enemy": [
        "196,97"
    ],
    "{:d}% Chance to cast level {:d} Might when you Kill an Enemy": [
        "196,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer when you Kill an Enemy": [
        "196,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire when you Kill an Enemy": [
        "196,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt when you Kill an Enemy": [
        "196,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire when you Kill an Enemy": [
        "196,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns when you Kill an Enemy": [
        "196,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance when you Kill an Enemy": [
        "196,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold when you Kill an Enemy": [
        "196,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal when you Kill an Enemy": [
        "196,106"
    ],
    "{:d}% Chance to cast level {:d} Charge when you Kill an Enemy": [
        "196,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim when you Kill an Enemy": [
        "196,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing when you Kill an Enemy": [
        "196,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning when you Kill an Enemy": [
        "196,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance when you Kill an Enemy": [
        "196,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer when you Kill an Enemy": [
        "196,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration when you Kill an Enemy": [
        "196,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze when you Kill an Enemy": [
        "196,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor when you Kill an Enemy": [
        "196,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion when you Kill an Enemy": [
        "196,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield when you Kill an Enemy": [
        "196,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock when you Kill an Enemy": [
        "196,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary when you Kill an Enemy": [
        "196,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation when you Kill an Enemy": [
        "196,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens when you Kill an Enemy": [
        "196,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism when you Kill an Enemy": [
        "196,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction when you Kill an Enemy": [
        "196,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption when you Kill an Enemy": [
        "196,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation when you Kill an Enemy": [
        "196,125"
    ],
    "{:d}% Chance to cast level {:d} Bash when you Kill an Enemy": [
        "196,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery when you Kill an Enemy": [
        "196,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery when you Kill an Enemy": [
        "196,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery when you Kill an Enemy": [
        "196,129"
    ],
    "{:d}% Chance to cast level {:d} Howl when you Kill an Enemy": [
        "196,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion when you Kill an Enemy": [
        "196,131"
    ],
    "{:d}% Chance to cast level {:d} Leap when you Kill an Enemy": [
        "196,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing when you Kill an Enemy": [
        "196,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery when you Kill an Enemy": [
        "196,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery when you Kill an Enemy": [
        "196,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery when you Kill an Enemy": [
        "196,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt when you Kill an Enemy": [
        "196,137"
    ],
    "{:d}% Chance to cast level {:d} Shout when you Kill an Enemy": [
        "196,138"
    ],
    "{:d}% Chance to cast level {:d} Stun when you Kill an Enemy": [
        "196,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw when you Kill an Enemy": [
        "196,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina when you Kill an Enemy": [
        "196,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item when you Kill an Enemy": [
        "196,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack when you Kill an Enemy": [
        "196,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate when you Kill an Enemy": [
        "196,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin when you Kill an Enemy": [
        "196,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry when you Kill an Enemy": [
        "196,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy when you Kill an Enemy": [
        "196,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed when you Kill an Enemy": [
        "196,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders when you Kill an Enemy": [
        "196,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward when you Kill an Enemy": [
        "196,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind when you Kill an Enemy": [
        "196,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk when you Kill an Enemy": [
        "196,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance when you Kill an Enemy": [
        "196,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry when you Kill an Enemy": [
        "196,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command when you Kill an Enemy": [
        "196,155"
    ],
    "{:d}% Chance to cast level {:d} Raven when you Kill an Enemy": [
        "196,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper when you Kill an Enemy": [
        "196,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf when you Kill an Enemy": [
        "196,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy when you Kill an Enemy": [
        "196,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm when you Kill an Enemy": [
        "196,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage when you Kill an Enemy": [
        "196,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf when you Kill an Enemy": [
        "196,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear when you Kill an Enemy": [
        "196,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder when you Kill an Enemy": [
        "196,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast when you Kill an Enemy": [
        "196,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine when you Kill an Enemy": [
        "196,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage when you Kill an Enemy": [
        "196,232"
    ],
    "{:d}% Chance to cast level {:d} Maul when you Kill an Enemy": [
        "196,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure when you Kill an Enemy": [
        "196,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor when you Kill an Enemy": [
        "196,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine when you Kill an Enemy": [
        "196,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf when you Kill an Enemy": [
        "196,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies when you Kill an Enemy": [
        "196,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws when you Kill an Enemy": [
        "196,239"
    ],
    "{:d}% Chance to cast level {:d} Twister when you Kill an Enemy": [
        "196,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper when you Kill an Enemy": [
        "196,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger when you Kill an Enemy": [
        "196,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave when you Kill an Enemy": [
        "196,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano when you Kill an Enemy": [
        "196,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado when you Kill an Enemy": [
        "196,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs when you Kill an Enemy": [
        "196,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly when you Kill an Enemy": [
        "196,247"
    ],
    "{:d}% Chance to cast level {:d} Fury when you Kill an Enemy": [
        "196,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon when you Kill an Enemy": [
        "196,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane when you Kill an Enemy": [
        "196,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast when you Kill an Enemy": [
        "196,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery when you Kill an Enemy": [
        "196,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer when you Kill an Enemy": [
        "196,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike when you Kill an Enemy": [
        "196,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon when you Kill an Enemy": [
        "196,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web when you Kill an Enemy": [
        "196,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel when you Kill an Enemy": [
        "196,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed when you Kill an Enemy": [
        "196,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire when you Kill an Enemy": [
        "196,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw when you Kill an Enemy": [
        "196,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry when you Kill an Enemy": [
        "196,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire when you Kill an Enemy": [
        "196,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block when you Kill an Enemy": [
        "196,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows when you Kill an Enemy": [
        "196,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike when you Kill an Enemy": [
        "196,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury when you Kill an Enemy": [
        "196,266"
    ],
    "{:d}% Chance to cast level {:d} Fade when you Kill an Enemy": [
        "196,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior when you Kill an Enemy": [
        "196,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder when you Kill an Enemy": [
        "196,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail when you Kill an Enemy": [
        "196,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry when you Kill an Enemy": [
        "196,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno when you Kill an Enemy": [
        "196,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast when you Kill an Enemy": [
        "196,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice when you Kill an Enemy": [
        "196,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight when you Kill an Enemy": [
        "196,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry when you Kill an Enemy": [
        "196,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield when you Kill an Enemy": [
        "196,277"
    ],
    "{:d}% Chance to cast level {:d} Venom when you Kill an Enemy": [
        "196,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master when you Kill an Enemy": [
        "196,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike when you Kill an Enemy": [
        "196,280"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow when you Die": [
        "197,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow when you Die": [
        "197,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight when you Die": [
        "197,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike when you Die": [
        "197,9"
    ],
    "{:d}% Chance to cast level {:d} Jab when you Die": [
        "197,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow when you Die": [
        "197,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot when you Die": [
        "197,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge when you Die": [
        "197,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike when you Die": [
        "197,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin when you Die": [
        "197,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow when you Die": [
        "197,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles when you Die": [
        "197,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid when you Die": [
        "197,18"
    ],
    "{:d}% Chance to cast level {:d} Impale when you Die": [
        "197,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt when you Die": [
        "197,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow when you Die": [
        "197,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow when you Die": [
        "197,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate when you Die": [
        "197,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike when you Die": [
        "197,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin when you Die": [
        "197,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe when you Die": [
        "197,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow when you Die": [
        "197,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy when you Die": [
        "197,28"
    ],
    "{:d}% Chance to cast level {:d} Evade when you Die": [
        "197,29"
    ],
    "{:d}% Chance to cast level {:d} Fend when you Die": [
        "197,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow when you Die": [
        "197,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie when you Die": [
        "197,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce when you Die": [
        "197,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike when you Die": [
        "197,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury when you Die": [
        "197,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt when you Die": [
        "197,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth when you Die": [
        "197,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt when you Die": [
        "197,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt when you Die": [
        "197,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor when you Die": [
        "197,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno when you Die": [
        "197,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field when you Die": [
        "197,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis when you Die": [
        "197,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova when you Die": [
        "197,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast when you Die": [
        "197,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze when you Die": [
        "197,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball when you Die": [
        "197,47"
    ],
    "{:d}% Chance to cast level {:d} Nova when you Die": [
        "197,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning when you Die": [
        "197,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor when you Die": [
        "197,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall when you Die": [
        "197,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant when you Die": [
        "197,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning when you Die": [
        "197,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport when you Die": [
        "197,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike when you Die": [
        "197,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor when you Die": [
        "197,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm when you Die": [
        "197,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield when you Die": [
        "197,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard when you Die": [
        "197,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor when you Die": [
        "197,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery when you Die": [
        "197,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra when you Die": [
        "197,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery when you Die": [
        "197,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb when you Die": [
        "197,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery when you Die": [
        "197,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage when you Die": [
        "197,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth when you Die": [
        "197,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor when you Die": [
        "197,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery when you Die": [
        "197,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton when you Die": [
        "197,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision when you Die": [
        "197,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken when you Die": [
        "197,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger when you Die": [
        "197,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion when you Die": [
        "197,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem when you Die": [
        "197,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden when you Die": [
        "197,76"
    ],
    "{:d}% Chance to cast level {:d} Terror when you Die": [
        "197,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall when you Die": [
        "197,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery when you Die": [
        "197,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage when you Die": [
        "197,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse when you Die": [
        "197,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap when you Die": [
        "197,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion when you Die": [
        "197,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear when you Die": [
        "197,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem when you Die": [
        "197,85"
    ],
    "{:d}% Chance to cast level {:d} Attract when you Die": [
        "197,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify when you Die": [
        "197,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison when you Die": [
        "197,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist when you Die": [
        "197,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem when you Die": [
        "197,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist when you Die": [
        "197,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova when you Die": [
        "197,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit when you Die": [
        "197,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem when you Die": [
        "197,94"
    ],
    "{:d}% Chance to cast level {:d} Revive when you Die": [
        "197,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice when you Die": [
        "197,96"
    ],
    "{:d}% Chance to cast level {:d} Smite when you Die": [
        "197,97"
    ],
    "{:d}% Chance to cast level {:d} Might when you Die": [
        "197,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer when you Die": [
        "197,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire when you Die": [
        "197,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt when you Die": [
        "197,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire when you Die": [
        "197,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns when you Die": [
        "197,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance when you Die": [
        "197,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold when you Die": [
        "197,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal when you Die": [
        "197,106"
    ],
    "{:d}% Chance to cast level {:d} Charge when you Die": [
        "197,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim when you Die": [
        "197,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing when you Die": [
        "197,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning when you Die": [
        "197,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance when you Die": [
        "197,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer when you Die": [
        "197,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration when you Die": [
        "197,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze when you Die": [
        "197,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor when you Die": [
        "197,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion when you Die": [
        "197,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield when you Die": [
        "197,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock when you Die": [
        "197,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary when you Die": [
        "197,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation when you Die": [
        "197,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens when you Die": [
        "197,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism when you Die": [
        "197,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction when you Die": [
        "197,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption when you Die": [
        "197,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation when you Die": [
        "197,125"
    ],
    "{:d}% Chance to cast level {:d} Bash when you Die": [
        "197,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery when you Die": [
        "197,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery when you Die": [
        "197,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery when you Die": [
        "197,129"
    ],
    "{:d}% Chance to cast level {:d} Howl when you Die": [
        "197,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion when you Die": [
        "197,131"
    ],
    "{:d}% Chance to cast level {:d} Leap when you Die": [
        "197,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing when you Die": [
        "197,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery when you Die": [
        "197,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery when you Die": [
        "197,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery when you Die": [
        "197,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt when you Die": [
        "197,137"
    ],
    "{:d}% Chance to cast level {:d} Shout when you Die": [
        "197,138"
    ],
    "{:d}% Chance to cast level {:d} Stun when you Die": [
        "197,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw when you Die": [
        "197,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina when you Die": [
        "197,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item when you Die": [
        "197,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack when you Die": [
        "197,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate when you Die": [
        "197,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin when you Die": [
        "197,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry when you Die": [
        "197,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy when you Die": [
        "197,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed when you Die": [
        "197,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders when you Die": [
        "197,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward when you Die": [
        "197,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind when you Die": [
        "197,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk when you Die": [
        "197,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance when you Die": [
        "197,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry when you Die": [
        "197,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command when you Die": [
        "197,155"
    ],
    "{:d}% Chance to cast level {:d} Raven when you Die": [
        "197,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper when you Die": [
        "197,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf when you Die": [
        "197,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy when you Die": [
        "197,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm when you Die": [
        "197,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage when you Die": [
        "197,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf when you Die": [
        "197,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear when you Die": [
        "197,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder when you Die": [
        "197,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast when you Die": [
        "197,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine when you Die": [
        "197,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage when you Die": [
        "197,232"
    ],
    "{:d}% Chance to cast level {:d} Maul when you Die": [
        "197,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure when you Die": [
        "197,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor when you Die": [
        "197,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine when you Die": [
        "197,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf when you Die": [
        "197,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies when you Die": [
        "197,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws when you Die": [
        "197,239"
    ],
    "{:d}% Chance to cast level {:d} Twister when you Die": [
        "197,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper when you Die": [
        "197,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger when you Die": [
        "197,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave when you Die": [
        "197,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano when you Die": [
        "197,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado when you Die": [
        "197,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs when you Die": [
        "197,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly when you Die": [
        "197,247"
    ],
    "{:d}% Chance to cast level {:d} Fury when you Die": [
        "197,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon when you Die": [
        "197,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane when you Die": [
        "197,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast when you Die": [
        "197,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery when you Die": [
        "197,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer when you Die": [
        "197,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike when you Die": [
        "197,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon when you Die": [
        "197,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web when you Die": [
        "197,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel when you Die": [
        "197,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed when you Die": [
        "197,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire when you Die": [
        "197,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw when you Die": [
        "197,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry when you Die": [
        "197,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire when you Die": [
        "197,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block when you Die": [
        "197,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows when you Die": [
        "197,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike when you Die": [
        "197,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury when you Die": [
        "197,266"
    ],
    "{:d}% Chance to cast level {:d} Fade when you Die": [
        "197,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior when you Die": [
        "197,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder when you Die": [
        "197,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail when you Die": [
        "197,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry when you Die": [
        "197,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno when you Die": [
        "197,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast when you Die": [
        "197,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice when you Die": [
        "197,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight when you Die": [
        "197,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry when you Die": [
        "197,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield when you Die": [
        "197,277"
    ],
    "{:d}% Chance to cast level {:d} Venom when you Die": [
        "197,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master when you Die": [
        "197,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike when you Die": [
        "197,280"
    ],
    "{:d}% Chance to cast level {:d} Magic Arrow when you Level-Up": [
        "199,6"
    ],
    "{:d}% Chance to cast level {:d} Fire Arrow when you Level-Up": [
        "199,7"
    ],
    "{:d}% Chance to cast level {:d} Inner Sight when you Level-Up": [
        "199,8"
    ],
    "{:d}% Chance to cast level {:d} Critical Strike when you Level-Up": [
        "199,9"
    ],
    "{:d}% Chance to cast level {:d} Jab when you Level-Up": [
        "199,10"
    ],
    "{:d}% Chance to cast level {:d} Cold Arrow when you Level-Up": [
        "199,11"
    ],
    "{:d}% Chance to cast level {:d} Multiple Shot when you Level-Up": [
        "199,12"
    ],
    "{:d}% Chance to cast level {:d} Dodge when you Level-Up": [
        "199,13"
    ],
    "{:d}% Chance to cast level {:d} Power Strike when you Level-Up": [
        "199,14"
    ],
    "{:d}% Chance to cast level {:d} Poison Javelin when you Level-Up": [
        "199,15"
    ],
    "{:d}% Chance to cast level {:d} Exploding Arrow when you Level-Up": [
        "199,16"
    ],
    "{:d}% Chance to cast level {:d} Slow Missiles when you Level-Up": [
        "199,17"
    ],
    "{:d}% Chance to cast level {:d} Avoid when you Level-Up": [
        "199,18"
    ],
    "{:d}% Chance to cast level {:d} Impale when you Level-Up": [
        "199,19"
    ],
    "{:d}% Chance to cast level {:d} Lightning Bolt when you Level-Up": [
        "199,20"
    ],
    "{:d}% Chance to cast level {:d} Ice Arrow when you Level-Up": [
        "199,21"
    ],
    "{:d}% Chance to cast level {:d} Guided Arrow when you Level-Up": [
        "199,22"
    ],
    "{:d}% Chance to cast level {:d} Penetrate when you Level-Up": [
        "199,23"
    ],
    "{:d}% Chance to cast level {:d} Charged Strike when you Level-Up": [
        "199,24"
    ],
    "{:d}% Chance to cast level {:d} Plague Javelin when you Level-Up": [
        "199,25"
    ],
    "{:d}% Chance to cast level {:d} Strafe when you Level-Up": [
        "199,26"
    ],
    "{:d}% Chance to cast level {:d} Immolation Arrow when you Level-Up": [
        "199,27"
    ],
    "{:d}% Chance to cast level {:d} Decoy when you Level-Up": [
        "199,28"
    ],
    "{:d}% Chance to cast level {:d} Evade when you Level-Up": [
        "199,29"
    ],
    "{:d}% Chance to cast level {:d} Fend when you Level-Up": [
        "199,30"
    ],
    "{:d}% Chance to cast level {:d} Freezing Arrow when you Level-Up": [
        "199,31"
    ],
    "{:d}% Chance to cast level {:d} Valkyrie when you Level-Up": [
        "199,32"
    ],
    "{:d}% Chance to cast level {:d} Pierce when you Level-Up": [
        "199,33"
    ],
    "{:d}% Chance to cast level {:d} Lightning Strike when you Level-Up": [
        "199,34"
    ],
    "{:d}% Chance to cast level {:d} Lightning Fury when you Level-Up": [
        "199,35"
    ],
    "{:d}% Chance to cast level {:d} Fire Bolt when you Level-Up": [
        "199,36"
    ],
    "{:d}% Chance to cast level {:d} Warmth when you Level-Up": [
        "199,37"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt when you Level-Up": [
        "199,38"
    ],
    "{:d}% Chance to cast level {:d} Ice Bolt when you Level-Up": [
        "199,39"
    ],
    "{:d}% Chance to cast level {:d} Frozen Armor when you Level-Up": [
        "199,40"
    ],
    "{:d}% Chance to cast level {:d} Inferno when you Level-Up": [
        "199,41"
    ],
    "{:d}% Chance to cast level {:d} Static Field when you Level-Up": [
        "199,42"
    ],
    "{:d}% Chance to cast level {:d} Telekinesis when you Level-Up": [
        "199,43"
    ],
    "{:d}% Chance to cast level {:d} Frost Nova when you Level-Up": [
        "199,44"
    ],
    "{:d}% Chance to cast level {:d} Ice Blast when you Level-Up": [
        "199,45"
    ],
    "{:d}% Chance to cast level {:d} Blaze when you Level-Up": [
        "199,46"
    ],
    "{:d}% Chance to cast level {:d} Fire Ball when you Level-Up": [
        "199,47"
    ],
    "{:d}% Chance to cast level {:d} Nova when you Level-Up": [
        "199,48"
    ],
    "{:d}% Chance to cast level {:d} Lightning when you Level-Up": [
        "199,49"
    ],
    "{:d}% Chance to cast level {:d} Shiver Armor when you Level-Up": [
        "199,50"
    ],
    "{:d}% Chance to cast level {:d} Fire Wall when you Level-Up": [
        "199,51"
    ],
    "{:d}% Chance to cast level {:d} Enchant when you Level-Up": [
        "199,52"
    ],
    "{:d}% Chance to cast level {:d} Chain Lightning when you Level-Up": [
        "199,53"
    ],
    "{:d}% Chance to cast level {:d} Teleport when you Level-Up": [
        "199,54"
    ],
    "{:d}% Chance to cast level {:d} Glacial Spike when you Level-Up": [
        "199,55"
    ],
    "{:d}% Chance to cast level {:d} Meteor when you Level-Up": [
        "199,56"
    ],
    "{:d}% Chance to cast level {:d} Thunder Storm when you Level-Up": [
        "199,57"
    ],
    "{:d}% Chance to cast level {:d} Energy Shield when you Level-Up": [
        "199,58"
    ],
    "{:d}% Chance to cast level {:d} Blizzard when you Level-Up": [
        "199,59"
    ],
    "{:d}% Chance to cast level {:d} Chilling Armor when you Level-Up": [
        "199,60"
    ],
    "{:d}% Chance to cast level {:d} Fire Mastery when you Level-Up": [
        "199,61"
    ],
    "{:d}% Chance to cast level {:d} Hydra when you Level-Up": [
        "199,62"
    ],
    "{:d}% Chance to cast level {:d} Lightning Mastery when you Level-Up": [
        "199,63"
    ],
    "{:d}% Chance to cast level {:d} Frozen Orb when you Level-Up": [
        "199,64"
    ],
    "{:d}% Chance to cast level {:d} Cold Mastery when you Level-Up": [
        "199,65"
    ],
    "{:d}% Chance to cast level {:d} Amplify Damage when you Level-Up": [
        "199,66"
    ],
    "{:d}% Chance to cast level {:d} Teeth when you Level-Up": [
        "199,67"
    ],
    "{:d}% Chance to cast level {:d} Bone Armor when you Level-Up": [
        "199,68"
    ],
    "{:d}% Chance to cast level {:d} Skeleton Mastery when you Level-Up": [
        "199,69"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeleton when you Level-Up": [
        "199,70"
    ],
    "{:d}% Chance to cast level {:d} Dim Vision when you Level-Up": [
        "199,71"
    ],
    "{:d}% Chance to cast level {:d} Weaken when you Level-Up": [
        "199,72"
    ],
    "{:d}% Chance to cast level {:d} Poison Dagger when you Level-Up": [
        "199,73"
    ],
    "{:d}% Chance to cast level {:d} Corpse Explosion when you Level-Up": [
        "199,74"
    ],
    "{:d}% Chance to cast level {:d} Clay Golem when you Level-Up": [
        "199,75"
    ],
    "{:d}% Chance to cast level {:d} Iron Maiden when you Level-Up": [
        "199,76"
    ],
    "{:d}% Chance to cast level {:d} Terror when you Level-Up": [
        "199,77"
    ],
    "{:d}% Chance to cast level {:d} Bone Wall when you Level-Up": [
        "199,78"
    ],
    "{:d}% Chance to cast level {:d} Golem Mastery when you Level-Up": [
        "199,79"
    ],
    "{:d}% Chance to cast level {:d} Raise Skeletal Mage when you Level-Up": [
        "199,80"
    ],
    "{:d}% Chance to cast level {:d} Confuse when you Level-Up": [
        "199,81"
    ],
    "{:d}% Chance to cast level {:d} Life Tap when you Level-Up": [
        "199,82"
    ],
    "{:d}% Chance to cast level {:d} Poison Explosion when you Level-Up": [
        "199,83"
    ],
    "{:d}% Chance to cast level {:d} Bone Spear when you Level-Up": [
        "199,84"
    ],
    "{:d}% Chance to cast level {:d} Blood Golem when you Level-Up": [
        "199,85"
    ],
    "{:d}% Chance to cast level {:d} Attract when you Level-Up": [
        "199,86"
    ],
    "{:d}% Chance to cast level {:d} Decrepify when you Level-Up": [
        "199,87"
    ],
    "{:d}% Chance to cast level {:d} Bone Prison when you Level-Up": [
        "199,88"
    ],
    "{:d}% Chance to cast level {:d} Summon Resist when you Level-Up": [
        "199,89"
    ],
    "{:d}% Chance to cast level {:d} Iron Golem when you Level-Up": [
        "199,90"
    ],
    "{:d}% Chance to cast level {:d} Lower Resist when you Level-Up": [
        "199,91"
    ],
    "{:d}% Chance to cast level {:d} Poison Nova when you Level-Up": [
        "199,92"
    ],
    "{:d}% Chance to cast level {:d} Bone Spirit when you Level-Up": [
        "199,93"
    ],
    "{:d}% Chance to cast level {:d} Fire Golem when you Level-Up": [
        "199,94"
    ],
    "{:d}% Chance to cast level {:d} Revive when you Level-Up": [
        "199,95"
    ],
    "{:d}% Chance to cast level {:d} Sacrifice when you Level-Up": [
        "199,96"
    ],
    "{:d}% Chance to cast level {:d} Smite when you Level-Up": [
        "199,97"
    ],
    "{:d}% Chance to cast level {:d} Might when you Level-Up": [
        "199,98"
    ],
    "{:d}% Chance to cast level {:d} Prayer when you Level-Up": [
        "199,99"
    ],
    "{:d}% Chance to cast level {:d} Resist Fire when you Level-Up": [
        "199,100"
    ],
    "{:d}% Chance to cast level {:d} Holy Bolt when you Level-Up": [
        "199,101"
    ],
    "{:d}% Chance to cast level {:d} Holy Fire when you Level-Up": [
        "199,102"
    ],
    "{:d}% Chance to cast level {:d} Thorns when you Level-Up": [
        "199,103"
    ],
    "{:d}% Chance to cast level {:d} Defiance when you Level-Up": [
        "199,104"
    ],
    "{:d}% Chance to cast level {:d} Resist Cold when you Level-Up": [
        "199,105"
    ],
    "{:d}% Chance to cast level {:d} Zeal when you Level-Up": [
        "199,106"
    ],
    "{:d}% Chance to cast level {:d} Charge when you Level-Up": [
        "199,107"
    ],
    "{:d}% Chance to cast level {:d} Blessed Aim when you Level-Up": [
        "199,108"
    ],
    "{:d}% Chance to cast level {:d} Cleansing when you Level-Up": [
        "199,109"
    ],
    "{:d}% Chance to cast level {:d} Resist Lightning when you Level-Up": [
        "199,110"
    ],
    "{:d}% Chance to cast level {:d} Vengeance when you Level-Up": [
        "199,111"
    ],
    "{:d}% Chance to cast level {:d} Blessed Hammer when you Level-Up": [
        "199,112"
    ],
    "{:d}% Chance to cast level {:d} Concentration when you Level-Up": [
        "199,113"
    ],
    "{:d}% Chance to cast level {:d} Holy Freeze when you Level-Up": [
        "199,114"
    ],
    "{:d}% Chance to cast level {:d} Vigor when you Level-Up": [
        "199,115"
    ],
    "{:d}% Chance to cast level {:d} Conversion when you Level-Up": [
        "199,116"
    ],
    "{:d}% Chance to cast level {:d} Holy Shield when you Level-Up": [
        "199,117"
    ],
    "{:d}% Chance to cast level {:d} Holy Shock when you Level-Up": [
        "199,118"
    ],
    "{:d}% Chance to cast level {:d} Sanctuary when you Level-Up": [
        "199,119"
    ],
    "{:d}% Chance to cast level {:d} Meditation when you Level-Up": [
        "199,120"
    ],
    "{:d}% Chance to cast level {:d} Fist of the Heavens when you Level-Up": [
        "199,121"
    ],
    "{:d}% Chance to cast level {:d} Fanaticism when you Level-Up": [
        "199,122"
    ],
    "{:d}% Chance to cast level {:d} Conviction when you Level-Up": [
        "199,123"
    ],
    "{:d}% Chance to cast level {:d} Redemption when you Level-Up": [
        "199,124"
    ],
    "{:d}% Chance to cast level {:d} Salvation when you Level-Up": [
        "199,125"
    ],
    "{:d}% Chance to cast level {:d} Bash when you Level-Up": [
        "199,126"
    ],
    "{:d}% Chance to cast level {:d} Blade Mastery when you Level-Up": [
        "199,127"
    ],
    "{:d}% Chance to cast level {:d} Axe Mastery when you Level-Up": [
        "199,128"
    ],
    "{:d}% Chance to cast level {:d} Mace Mastery when you Level-Up": [
        "199,129"
    ],
    "{:d}% Chance to cast level {:d} Howl when you Level-Up": [
        "199,130"
    ],
    "{:d}% Chance to cast level {:d} Find Potion when you Level-Up": [
        "199,131"
    ],
    "{:d}% Chance to cast level {:d} Leap when you Level-Up": [
        "199,132"
    ],
    "{:d}% Chance to cast level {:d} Double Swing when you Level-Up": [
        "199,133"
    ],
    "{:d}% Chance to cast level {:d} Polearm Mastery when you Level-Up": [
        "199,134"
    ],
    "{:d}% Chance to cast level {:d} Throwing Mastery when you Level-Up": [
        "199,135"
    ],
    "{:d}% Chance to cast level {:d} Spear Mastery when you Level-Up": [
        "199,136"
    ],
    "{:d}% Chance to cast level {:d} Taunt when you Level-Up": [
        "199,137"
    ],
    "{:d}% Chance to cast level {:d} Shout when you Level-Up": [
        "199,138"
    ],
    "{:d}% Chance to cast level {:d} Stun when you Level-Up": [
        "199,139"
    ],
    "{:d}% Chance to cast level {:d} Double Throw when you Level-Up": [
        "199,140"
    ],
    "{:d}% Chance to cast level {:d} Increased Stamina when you Level-Up": [
        "199,141"
    ],
    "{:d}% Chance to cast level {:d} Find Item when you Level-Up": [
        "199,142"
    ],
    "{:d}% Chance to cast level {:d} Leap Attack when you Level-Up": [
        "199,143"
    ],
    "{:d}% Chance to cast level {:d} Concentrate when you Level-Up": [
        "199,144"
    ],
    "{:d}% Chance to cast level {:d} Iron Skin when you Level-Up": [
        "199,145"
    ],
    "{:d}% Chance to cast level {:d} Battle Cry when you Level-Up": [
        "199,146"
    ],
    "{:d}% Chance to cast level {:d} Frenzy when you Level-Up": [
        "199,147"
    ],
    "{:d}% Chance to cast level {:d} Increased Speed when you Level-Up": [
        "199,148"
    ],
    "{:d}% Chance to cast level {:d} Battle Orders when you Level-Up": [
        "199,149"
    ],
    "{:d}% Chance to cast level {:d} Grim Ward when you Level-Up": [
        "199,150"
    ],
    "{:d}% Chance to cast level {:d} Whirlwind when you Level-Up": [
        "199,151"
    ],
    "{:d}% Chance to cast level {:d} Berserk when you Level-Up": [
        "199,152"
    ],
    "{:d}% Chance to cast level {:d} Natural Resistance when you Level-Up": [
        "199,153"
    ],
    "{:d}% Chance to cast level {:d} War Cry when you Level-Up": [
        "199,154"
    ],
    "{:d}% Chance to cast level {:d} Battle Command when you Level-Up": [
        "199,155"
    ],
    "{:d}% Chance to cast level {:d} Raven when you Level-Up": [
        "199,221"
    ],
    "{:d}% Chance to cast level {:d} Poison Creeper when you Level-Up": [
        "199,222"
    ],
    "{:d}% Chance to cast level {:d} Werewolf when you Level-Up": [
        "199,223"
    ],
    "{:d}% Chance to cast level {:d} Lycanthropy when you Level-Up": [
        "199,224"
    ],
    "{:d}% Chance to cast level {:d} Firestorm when you Level-Up": [
        "199,225"
    ],
    "{:d}% Chance to cast level {:d} Oak Sage when you Level-Up": [
        "199,226"
    ],
    "{:d}% Chance to cast level {:d} Summon Spirit Wolf when you Level-Up": [
        "199,227"
    ],
    "{:d}% Chance to cast level {:d} Werebear when you Level-Up": [
        "199,228"
    ],
    "{:d}% Chance to cast level {:d} Molten Boulder when you Level-Up": [
        "199,229"
    ],
    "{:d}% Chance to cast level {:d} Arctic Blast when you Level-Up": [
        "199,230"
    ],
    "{:d}% Chance to cast level {:d} Carrion Vine when you Level-Up": [
        "199,231"
    ],
    "{:d}% Chance to cast level {:d} Feral Rage when you Level-Up": [
        "199,232"
    ],
    "{:d}% Chance to cast level {:d} Maul when you Level-Up": [
        "199,233"
    ],
    "{:d}% Chance to cast level {:d} Fissure when you Level-Up": [
        "199,234"
    ],
    "{:d}% Chance to cast level {:d} Cyclone Armor when you Level-Up": [
        "199,235"
    ],
    "{:d}% Chance to cast level {:d} Heart of Wolverine when you Level-Up": [
        "199,236"
    ],
    "{:d}% Chance to cast level {:d} Summon Dire Wolf when you Level-Up": [
        "199,237"
    ],
    "{:d}% Chance to cast level {:d} Rabies when you Level-Up": [
        "199,238"
    ],
    "{:d}% Chance to cast level {:d} Fire Claws when you Level-Up": [
        "199,239"
    ],
    "{:d}% Chance to cast level {:d} Twister when you Level-Up": [
        "199,240"
    ],
    "{:d}% Chance to cast level {:d} Solar Creeper when you Level-Up": [
        "199,241"
    ],
    "{:d}% Chance to cast level {:d} Hunger when you Level-Up": [
        "199,242"
    ],
    "{:d}% Chance to cast level {:d} Shock Wave when you Level-Up": [
        "199,243"
    ],
    "{:d}% Chance to cast level {:d} Volcano when you Level-Up": [
        "199,244"
    ],
    "{:d}% Chance to cast level {:d} Tornado when you Level-Up": [
        "199,245"
    ],
    "{:d}% Chance to cast level {:d} Spirit of Barbs when you Level-Up": [
        "199,246"
    ],
    "{:d}% Chance to cast level {:d} Summon Grizzly when you Level-Up": [
        "199,247"
    ],
    "{:d}% Chance to cast level {:d} Fury when you Level-Up": [
        "199,248"
    ],
    "{:d}% Chance to cast level {:d} Armageddon when you Level-Up": [
        "199,249"
    ],
    "{:d}% Chance to cast level {:d} Hurricane when you Level-Up": [
        "199,250"
    ],
    "{:d}% Chance to cast level {:d} Fire Blast when you Level-Up": [
        "199,251"
    ],
    "{:d}% Chance to cast level {:d} Claw Mastery when you Level-Up": [
        "199,252"
    ],
    "{:d}% Chance to cast level {:d} Psychic Hammer when you Level-Up": [
        "199,253"
    ],
    "{:d}% Chance to cast level {:d} Tiger Strike when you Level-Up": [
        "199,254"
    ],
    "{:d}% Chance to cast level {:d} Dragon Talon when you Level-Up": [
        "199,255"
    ],
    "{:d}% Chance to cast level {:d} Shock Web when you Level-Up": [
        "199,256"
    ],
    "{:d}% Chance to cast level {:d} Blade Sentinel when you Level-Up": [
        "199,257"
    ],
    "{:d}% Chance to cast level {:d} Burst of Speed when you Level-Up": [
        "199,258"
    ],
    "{:d}% Chance to cast level {:d} Fists of Fire when you Level-Up": [
        "199,259"
    ],
    "{:d}% Chance to cast level {:d} Dragon Claw when you Level-Up": [
        "199,260"
    ],
    "{:d}% Chance to cast level {:d} Charged Bolt Sentry when you Level-Up": [
        "199,261"
    ],
    "{:d}% Chance to cast level {:d} Wake of Fire when you Level-Up": [
        "199,262"
    ],
    "{:d}% Chance to cast level {:d} Weapon Block when you Level-Up": [
        "199,263"
    ],
    "{:d}% Chance to cast level {:d} Cloak of Shadows when you Level-Up": [
        "199,264"
    ],
    "{:d}% Chance to cast level {:d} Cobra Strike when you Level-Up": [
        "199,265"
    ],
    "{:d}% Chance to cast level {:d} Blade Fury when you Level-Up": [
        "199,266"
    ],
    "{:d}% Chance to cast level {:d} Fade when you Level-Up": [
        "199,267"
    ],
    "{:d}% Chance to cast level {:d} Shadow Warrior when you Level-Up": [
        "199,268"
    ],
    "{:d}% Chance to cast level {:d} Claws of Thunder when you Level-Up": [
        "199,269"
    ],
    "{:d}% Chance to cast level {:d} Dragon Tail when you Level-Up": [
        "199,270"
    ],
    "{:d}% Chance to cast level {:d} Lightning Sentry when you Level-Up": [
        "199,271"
    ],
    "{:d}% Chance to cast level {:d} Wake of Inferno when you Level-Up": [
        "199,272"
    ],
    "{:d}% Chance to cast level {:d} Mind Blast when you Level-Up": [
        "199,273"
    ],
    "{:d}% Chance to cast level {:d} Blades of Ice when you Level-Up": [
        "199,274"
    ],
    "{:d}% Chance to cast level {:d} Dragon Flight when you Level-Up": [
        "199,275"
    ],
    "{:d}% Chance to cast level {:d} Death Sentry when you Level-Up": [
        "199,276"
    ],
    "{:d}% Chance to cast level {:d} Blade Shield when you Level-Up": [
        "199,277"
    ],
    "{:d}% Chance to cast level {:d} Venom when you Level-Up": [
        "199,278"
    ],
    "{:d}% Chance to cast level {:d} Shadow Master when you Level-Up": [
        "199,279"
    ],
    "{:d}% Chance to cast level {:d} Phoenix Strike when you Level-Up": [
        "199,280"
    ],
    "Required Level: {:d}": [
        "92"
    ],
    "{:d} to Magic Arrow": [
        "97,6"
    ],
    "{:d} to Fire Arrow": [
        "97,7"
    ],
    "{:d} to Inner Sight": [
        "97,8"
    ],
    "{:d} to Critical Strike": [
        "97,9"
    ],
    "{:d} to Jab": [
        "97,10"
    ],
    "{:d} to Cold Arrow": [
        "97,11"
    ],
    "{:d} to Multiple Shot": [
        "97,12"
    ],
    "{:d} to Dodge": [
        "97,13"
    ],
    "{:d} to Power Strike": [
        "97,14"
    ],
    "{:d} to Poison Javelin": [
        "97,15"
    ],
    "{:d} to Exploding Arrow": [
        "97,16"
    ],
    "{:d} to Slow Missiles": [
        "97,17"
    ],
    "{:d} to Avoid": [
        "97,18"
    ],
    "{:d} to Impale": [
        "97,19"
    ],
    "{:d} to Lightning Bolt": [
        "97,20"
    ],
    "{:d} to Ice Arrow": [
        "97,21"
    ],
    "{:d} to Guided Arrow": [
        "97,22"
    ],
    "{:d} to Penetrate": [
        "97,23"
    ],
    "{:d} to Charged Strike": [
        "97,24"
    ],
    "{:d} to Plague Javelin": [
        "97,25"
    ],
    "{:d} to Strafe": [
        "97,26"
    ],
    "{:d} to Immolation Arrow": [
        "97,27"
    ],
    "{:d} to Decoy": [
        "97,28"
    ],
    "{:d} to Evade": [
        "97,29"
    ],
    "{:d} to Fend": [
        "97,30"
    ],
    "{:d} to Freezing Arrow": [
        "97,31"
    ],
    "{:d} to Valkyrie": [
        "97,32"
    ],
    "{:d} to Pierce": [
        "97,33"
    ],
    "{:d} to Lightning Strike": [
        "97,34"
    ],
    "{:d} to Lightning Fury": [
        "97,35"
    ],
    "{:d} to Fire Bolt": [
        "97,36"
    ],
    "{:d} to Warmth": [
        "97,37"
    ],
    "{:d} to Charged Bolt": [
        "97,38"
    ],
    "{:d} to Ice Bolt": [
        "97,39"
    ],
    "{:d} to Frozen Armor": [
        "97,40"
    ],
    "{:d} to Inferno": [
        "97,41"
    ],
    "{:d} to Static Field": [
        "97,42"
    ],
    "{:d} to Telekinesis": [
        "97,43"
    ],
    "{:d} to Frost Nova": [
        "97,44"
    ],
    "{:d} to Ice Blast": [
        "97,45"
    ],
    "{:d} to Blaze": [
        "97,46"
    ],
    "{:d} to Fire Ball": [
        "97,47"
    ],
    "{:d} to Nova": [
        "97,48"
    ],
    "{:d} to Lightning": [
        "97,49"
    ],
    "{:d} to Shiver Armor": [
        "97,50"
    ],
    "{:d} to Fire Wall": [
        "97,51"
    ],
    "{:d} to Enchant": [
        "97,52"
    ],
    "{:d} to Chain Lightning": [
        "97,53"
    ],
    "{:d} to Teleport": [
        "97,54"
    ],
    "{:d} to Glacial Spike": [
        "97,55"
    ],
    "{:d} to Meteor": [
        "97,56"
    ],
    "{:d} to Thunder Storm": [
        "97,57"
    ],
    "{:d} to Energy Shield": [
        "97,58"
    ],
    "{:d} to Blizzard": [
        "97,59"
    ],
    "{:d} to Chilling Armor": [
        "97,60"
    ],
    "{:d} to Fire Mastery": [
        "97,61"
    ],
    "{:d} to Hydra": [
        "97,62"
    ],
    "{:d} to Lightning Mastery": [
        "97,63"
    ],
    "{:d} to Frozen Orb": [
        "97,64"
    ],
    "{:d} to Cold Mastery": [
        "97,65"
    ],
    "{:d} to Amplify Damage": [
        "97,66"
    ],
    "{:d} to Teeth": [
        "97,67"
    ],
    "{:d} to Bone Armor": [
        "97,68"
    ],
    "{:d} to Skeleton Mastery": [
        "97,69"
    ],
    "{:d} to Raise Skeleton": [
        "97,70"
    ],
    "{:d} to Dim Vision": [
        "97,71"
    ],
    "{:d} to Weaken": [
        "97,72"
    ],
    "{:d} to Poison Dagger": [
        "97,73"
    ],
    "{:d} to Corpse Explosion": [
        "97,74"
    ],
    "{:d} to Clay Golem": [
        "97,75"
    ],
    "{:d} to Iron Maiden": [
        "97,76"
    ],
    "{:d} to Terror": [
        "97,77"
    ],
    "{:d} to Bone Wall": [
        "97,78"
    ],
    "{:d} to Golem Mastery": [
        "97,79"
    ],
    "{:d} to Raise Skeletal Mage": [
        "97,80"
    ],
    "{:d} to Confuse": [
        "97,81"
    ],
    "{:d} to Life Tap": [
        "97,82"
    ],
    "{:d} to Poison Explosion": [
        "97,83"
    ],
    "{:d} to Bone Spear": [
        "97,84"
    ],
    "{:d} to Blood Golem": [
        "97,85"
    ],
    "{:d} to Attract": [
        "97,86"
    ],
    "{:d} to Decrepify": [
        "97,87"
    ],
    "{:d} to Bone Prison": [
        "97,88"
    ],
    "{:d} to Summon Resist": [
        "97,89"
    ],
    "{:d} to Iron Golem": [
        "97,90"
    ],
    "{:d} to Lower Resist": [
        "97,91"
    ],
    "{:d} to Poison Nova": [
        "97,92"
    ],
    "{:d} to Bone Spirit": [
        "97,93"
    ],
    "{:d} to Fire Golem": [
        "97,94"
    ],
    "{:d} to Revive": [
        "97,95"
    ],
    "{:d} to Sacrifice": [
        "97,96"
    ],
    "{:d} to Smite": [
        "97,97"
    ],
    "{:d} to Might": [
        "97,98"
    ],
    "{:d} to Prayer": [
        "97,99"
    ],
    "{:d} to Resist Fire": [
        "97,100"
    ],
    "{:d} to Holy Bolt": [
        "97,101"
    ],
    "{:d} to Holy Fire": [
        "97,102"
    ],
    "{:d} to Thorns": [
        "97,103"
    ],
    "{:d} to Defiance": [
        "97,104"
    ],
    "{:d} to Resist Cold": [
        "97,105"
    ],
    "{:d} to Zeal": [
        "97,106"
    ],
    "{:d} to Charge": [
        "97,107"
    ],
    "{:d} to Blessed Aim": [
        "97,108"
    ],
    "{:d} to Cleansing": [
        "97,109"
    ],
    "{:d} to Resist Lightning": [
        "97,110"
    ],
    "{:d} to Vengeance": [
        "97,111"
    ],
    "{:d} to Blessed Hammer": [
        "97,112"
    ],
    "{:d} to Concentration": [
        "97,113"
    ],
    "{:d} to Holy Freeze": [
        "97,114"
    ],
    "{:d} to Vigor": [
        "97,115"
    ],
    "{:d} to Conversion": [
        "97,116"
    ],
    "{:d} to Holy Shield": [
        "97,117"
    ],
    "{:d} to Holy Shock": [
        "97,118"
    ],
    "{:d} to Sanctuary": [
        "97,119"
    ],
    "{:d} to Meditation": [
        "97,120"
    ],
    "{:d} to Fist of the Heavens": [
        "97,121"
    ],
    "{:d} to Fanaticism": [
        "97,122"
    ],
    "{:d} to Conviction": [
        "97,123"
    ],
    "{:d} to Redemption": [
        "97,124"
    ],
    "{:d} to Salvation": [
        "97,125"
    ],
    "{:d} to Bash": [
        "97,126"
    ],
    "{:d} to Blade Mastery": [
        "97,127"
    ],
    "{:d} to Axe Mastery": [
        "97,128"
    ],
    "{:d} to Mace Mastery": [
        "97,129"
    ],
    "{:d} to Howl": [
        "97,130"
    ],
    "{:d} to Find Potion": [
        "97,131"
    ],
    "{:d} to Leap": [
        "97,132"
    ],
    "{:d} to Double Swing": [
        "97,133"
    ],
    "{:d} to Polearm Mastery": [
        "97,134"
    ],
    "{:d} to Throwing Mastery": [
        "97,135"
    ],
    "{:d} to Spear Mastery": [
        "97,136"
    ],
    "{:d} to Taunt": [
        "97,137"
    ],
    "{:d} to Shout": [
        "97,138"
    ],
    "{:d} to Stun": [
        "97,139"
    ],
    "{:d} to Double Throw": [
        "97,140"
    ],
    "{:d} to Increased Stamina": [
        "97,141"
    ],
    "{:d} to Find Item": [
        "97,142"
    ],
    "{:d} to Leap Attack": [
        "97,143"
    ],
    "{:d} to Concentrate": [
        "97,144"
    ],
    "{:d} to Iron Skin": [
        "97,145"
    ],
    "{:d} to Battle Cry": [
        "97,146"
    ],
    "{:d} to Frenzy": [
        "97,147"
    ],
    "{:d} to Increased Speed": [
        "97,148"
    ],
    "{:d} to Battle Orders": [
        "97,149"
    ],
    "{:d} to Grim Ward": [
        "97,150"
    ],
    "{:d} to Whirlwind": [
        "97,151"
    ],
    "{:d} to Berserk": [
        "97,152"
    ],
    "{:d} to Natural Resistance": [
        "97,153"
    ],
    "{:d} to War Cry": [
        "97,154"
    ],
    "{:d} to Battle Command": [
        "97,155"
    ],
    "{:d} to Raven": [
        "97,221"
    ],
    "{:d} to Poison Creeper": [
        "97,222"
    ],
    "{:d} to Werewolf": [
        "97,223"
    ],
    "{:d} to Lycanthropy": [
        "97,224"
    ],
    "{:d} to Firestorm": [
        "97,225"
    ],
    "{:d} to Oak Sage": [
        "97,226"
    ],
    "{:d} to Summon Spirit Wolf": [
        "97,227"
    ],
    "{:d} to Werebear": [
        "97,228"
    ],
    "{:d} to Molten Boulder": [
        "97,229"
    ],
    "{:d} to Arctic Blast": [
        "97,230"
    ],
    "{:d} to Carrion Vine": [
        "97,231"
    ],
    "{:d} to Feral Rage": [
        "97,232"
    ],
    "{:d} to Maul": [
        "97,233"
    ],
    "{:d} to Fissure": [
        "97,234"
    ],
    "{:d} to Cyclone Armor": [
        "97,235"
    ],
    "{:d} to Heart of Wolverine": [
        "97,236"
    ],
    "{:d} to Summon Dire Wolf": [
        "97,237"
    ],
    "{:d} to Rabies": [
        "97,238"
    ],
    "{:d} to Fire Claws": [
        "97,239"
    ],
    "{:d} to Twister": [
        "97,240"
    ],
    "{:d} to Solar Creeper": [
        "97,241"
    ],
    "{:d} to Hunger": [
        "97,242"
    ],
    "{:d} to Shock Wave": [
        "97,243"
    ],
    "{:d} to Volcano": [
        "97,244"
    ],
    "{:d} to Tornado": [
        "97,245"
    ],
    "{:d} to Spirit of Barbs": [
        "97,246"
    ],
    "{:d} to Summon Grizzly": [
        "97,247"
    ],
    "{:d} to Fury": [
        "97,248"
    ],
    "{:d} to Armageddon": [
        "97,249"
    ],
    "{:d} to Hurricane": [
        "97,250"
    ],
    "{:d} to Fire Blast": [
        "97,251"
    ],
    "{:d} to Claw Mastery": [
        "97,252"
    ],
    "{:d} to Psychic Hammer": [
        "97,253"
    ],
    "{:d} to Tiger Strike": [
        "97,254"
    ],
    "{:d} to Dragon Talon": [
        "97,255"
    ],
    "{:d} to Shock Web": [
        "97,256"
    ],
    "{:d} to Blade Sentinel": [
        "97,257"
    ],
    "{:d} to Burst of Speed": [
        "97,258"
    ],
    "{:d} to Fists of Fire": [
        "97,259"
    ],
    "{:d} to Dragon Claw": [
        "97,260"
    ],
    "{:d} to Charged Bolt Sentry": [
        "97,261"
    ],
    "{:d} to Wake of Fire": [
        "97,262"
    ],
    "{:d} to Weapon Block": [
        "97,263"
    ],
    "{:d} to Cloak of Shadows": [
        "97,264"
    ],
    "{:d} to Cobra Strike": [
        "97,265"
    ],
    "{:d} to Blade Fury": [
        "97,266"
    ],
    "{:d} to Fade": [
        "97,267"
    ],
    "{:d} to Shadow Warrior": [
        "97,268"
    ],
    "{:d} to Claws of Thunder": [
        "97,269"
    ],
    "{:d} to Dragon Tail": [
        "97,270"
    ],
    "{:d} to Lightning Sentry": [
        "97,271"
    ],
    "{:d} to Wake of Inferno": [
        "97,272"
    ],
    "{:d} to Mind Blast": [
        "97,273"
    ],
    "{:d} to Blades of Ice": [
        "97,274"
    ],
    "{:d} to Dragon Flight": [
        "97,275"
    ],
    "{:d} to Death Sentry": [
        "97,276"
    ],
    "{:d} to Blade Shield": [
        "97,277"
    ],
    "{:d} to Venom": [
        "97,278"
    ],
    "{:d} to Shadow Master": [
        "97,279"
    ],
    "{:d} to Phoenix Strike": [
        "97,280"
    ],
    "{:d} to not Consume Quantity": [
        "205"
    ],
    "ETHEREAL (CANNOT BE REPAIRED), SOCKETED ({:d})": [
        "194"
    ],
    "{:d} Poison Damage over {:d} Seconds": [
        [
            "57",
            "58"
        ],
        "59"
    ],
    "One-Hand Damage: {:d} to {:d}": [
        "5000",
        "5001"
    ],
    "Two-Hand Damage: {:d} to {:d}": [
        "5000",
        "5001"
    ],
    "Throw Damage: {:d} to {:d}": [
        "5000",
        "5001"
    ],
    "Smite Damage: {:d} to {:d}": [
        "5000",
        "5001"
    ],
    "Quantity: {:d}": [
        "70"
    ],
    "Quantity: {:d} of {:d}": [
        "70",
        "5003"
    ],
    "Indestructible": [
        "5004"
    ],
    "Defense: {:d}": [
        "31"
    ],
    "{:d}% Enhanced Damage": [
        "5007"
    ],
    "{:d} to Summoning Skills (Necromancer Only)": [
        "188,21"
    ]
}

BNIP_ALIAS_STAT_PATTERNS_NO_INTS = dict(
    zip(
        list(
            map(
                lambda mystr: ''.join(filter(lambda x: not x.isdigit(), mystr)).replace('+','').replace('-','').replace('{:d}','').upper(),
                BNIP_ALIAS_STAT_PATTERNS.keys()
            )
        ),
        BNIP_ALIAS_STAT_PATTERNS.keys()
    )
)


BNIP_ITEM_TYPE_DATA = {
    "Cap": [
        "helm",
        "anyarmor"
    ],
    "Skull Cap": [
        "helm",
        "anyarmor"
    ],
    "Helm": [
        "helm",
        "anyarmor"
    ],
    "Full Helm": [
        "helm",
        "anyarmor"
    ],
    "Great Helm": [
        "helm",
        "anyarmor"
    ],
    "Crown": [
        "helm",
        "anyarmor"
    ],
    "Mask": [
        "helm",
        "anyarmor"
    ],
    "Quilted Armor": [
        "armor",
        "anyarmor"
    ],
    "Leather Armor": [
        "armor",
        "anyarmor"
    ],
    "Hard Leather Armor": [
        "armor",
        "anyarmor"
    ],
    "Studded Leather": [
        "armor",
        "anyarmor"
    ],
    "Ring Mail": [
        "armor",
        "anyarmor"
    ],
    "Scale Mail": [
        "armor",
        "anyarmor"
    ],
    "Chain Mail": [
        "armor",
        "anyarmor"
    ],
    "Breast Plate": [
        "armor",
        "anyarmor"
    ],
    "Splint Mail": [
        "armor",
        "anyarmor"
    ],
    "Plate Mail": [
        "armor",
        "anyarmor"
    ],
    "Field Plate": [
        "armor",
        "anyarmor"
    ],
    "Gothic Plate": [
        "armor",
        "anyarmor"
    ],
    "Full Plate Mail": [
        "armor",
        "anyarmor"
    ],
    "Ancient Armor": [
        "armor",
        "anyarmor"
    ],
    "Light Plate": [
        "armor",
        "anyarmor"
    ],
    "Buckler": [
        "shield",
        "anyshield"
    ],
    "Small Shield": [
        "shield",
        "anyshield"
    ],
    "Large Shield": [
        "shield",
        "anyshield"
    ],
    "Kite Shield": [
        "shield",
        "anyshield"
    ],
    "Tower Shield": [
        "shield",
        "anyshield"
    ],
    "Gothic Shield": [
        "shield",
        "anyshield"
    ],
    "Leather Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Heavy Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Chain Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Light Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "Boots": [
        "boots",
        "anyarmor"
    ],
    "Heavy Boots": [
        "boots",
        "anyarmor"
    ],
    "Chain Boots": [
        "boots",
        "anyarmor"
    ],
    "Light Plated Boots": [
        "boots",
        "anyarmor"
    ],
    "Greaves": [
        "boots",
        "anyarmor"
    ],
    "Sash": [
        "belt",
        "anyarmor"
    ],
    "Light Belt": [
        "belt",
        "anyarmor"
    ],
    "Belt": [
        "belt",
        "anyarmor"
    ],
    "Heavy Belt": [
        "belt",
        "anyarmor"
    ],
    "Plated Belt": [
        "belt",
        "anyarmor"
    ],
    "Bone Helm": [
        "helm",
        "anyarmor"
    ],
    "Bone Shield": [
        "shield",
        "anyshield"
    ],
    "Spiked Shield": [
        "shield",
        "anyshield"
    ],
    "War Hat": [
        "helm",
        "anyarmor"
    ],
    "Sallet": [
        "helm",
        "anyarmor"
    ],
    "Casque": [
        "helm",
        "anyarmor"
    ],
    "Basinet": [
        "helm",
        "anyarmor"
    ],
    "Winged Helm": [
        "helm",
        "anyarmor"
    ],
    "Grand Crown": [
        "helm",
        "anyarmor"
    ],
    "Death Mask": [
        "helm",
        "anyarmor"
    ],
    "Ghost Armor": [
        "armor",
        "anyarmor"
    ],
    "Serpentskin Armor": [
        "armor",
        "anyarmor"
    ],
    "Demonhide Armor": [
        "armor",
        "anyarmor"
    ],
    "Trellised Armor": [
        "armor",
        "anyarmor"
    ],
    "Linked Mail": [
        "armor",
        "anyarmor"
    ],
    "Tigulated Mail": [
        "armor",
        "anyarmor"
    ],
    "Mesh Armor": [
        "armor",
        "anyarmor"
    ],
    "Cuirass": [
        "armor",
        "anyarmor"
    ],
    "Russet Armor": [
        "armor",
        "anyarmor"
    ],
    "Templar Coat": [
        "armor",
        "anyarmor"
    ],
    "Sharktooth Armor": [
        "armor",
        "anyarmor"
    ],
    "Embossed Plate": [
        "armor",
        "anyarmor"
    ],
    "Chaos Armor": [
        "armor",
        "anyarmor"
    ],
    "Ornate Plate": [
        "armor",
        "anyarmor"
    ],
    "Mage Plate": [
        "armor",
        "anyarmor"
    ],
    "Defender": [
        "shield",
        "anyshield"
    ],
    "Round Shield": [
        "shield",
        "anyshield"
    ],
    "Scutum": [
        "shield",
        "anyshield"
    ],
    "Dragon Shield": [
        "shield",
        "anyshield"
    ],
    "Pavise": [
        "shield",
        "anyshield"
    ],
    "Ancient Shield": [
        "shield",
        "anyshield"
    ],
    "Demonhide Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Sharkskin Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Heavy Bracers": [
        "gloves",
        "anyarmor"
    ],
    "Battle Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "War Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "Demonhide Boots": [
        "boots",
        "anyarmor"
    ],
    "Sharkskin Boots": [
        "boots",
        "anyarmor"
    ],
    "Mesh Boots": [
        "boots",
        "anyarmor"
    ],
    "Battle Boots": [
        "boots",
        "anyarmor"
    ],
    "War Boots": [
        "boots",
        "anyarmor"
    ],
    "Demonhide Sash": [
        "belt",
        "anyarmor"
    ],
    "Sharkskin Belt": [
        "belt",
        "anyarmor"
    ],
    "Mesh Belt": [
        "belt",
        "anyarmor"
    ],
    "Battle Belt": [
        "belt",
        "anyarmor"
    ],
    "War Belt": [
        "belt",
        "anyarmor"
    ],
    "Grim Helm": [
        "helm",
        "anyarmor"
    ],
    "Grim Shield": [
        "shield",
        "anyshield"
    ],
    "Barbed Shield": [
        "shield",
        "anyshield"
    ],
    "Wolf Head": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Hawk Helm": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Antlers": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Falcon Mask": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Spirit Mask": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Jawbone Cap": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Fanged Helm": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Horned Helm": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Assault Helmet": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Avenger Guard": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Targe": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Rondache": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Heraldic Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Aerin Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Crown Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Preserved Head": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Zombie Head": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Unraveller Head": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Gargoyle Head": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Demon Head": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Circlet": [
        "circlet",
        "helm"
    ],
    "Coronet": [
        "circlet",
        "helm"
    ],
    "Tiara": [
        "circlet",
        "helm"
    ],
    "Diadem": [
        "circlet",
        "helm"
    ],
    "Shako": [
        "helm",
        "anyarmor"
    ],
    "Hydraskull": [
        "helm",
        "anyarmor"
    ],
    "Armet": [
        "helm",
        "anyarmor"
    ],
    "Giant Conch": [
        "helm",
        "anyarmor"
    ],
    "Spired Helm": [
        "helm",
        "anyarmor"
    ],
    "Corona": [
        "helm",
        "anyarmor"
    ],
    "Demonhead": [
        "helm",
        "anyarmor"
    ],
    "Dusk Shroud": [
        "armor",
        "anyarmor"
    ],
    "Wyrmhide": [
        "armor",
        "anyarmor"
    ],
    "Scarab Husk": [
        "armor",
        "anyarmor"
    ],
    "Wire Fleece": [
        "armor",
        "anyarmor"
    ],
    "Diamond Mail": [
        "armor",
        "anyarmor"
    ],
    "Loricated Mail": [
        "armor",
        "anyarmor"
    ],
    "Boneweave": [
        "armor",
        "anyarmor"
    ],
    "Great Hauberk": [
        "armor",
        "anyarmor"
    ],
    "Balrog Skin": [
        "armor",
        "anyarmor"
    ],
    "Hellforge Plate": [
        "armor",
        "anyarmor"
    ],
    "Kraken Shell": [
        "armor",
        "anyarmor"
    ],
    "Lacquered Plate": [
        "armor",
        "anyarmor"
    ],
    "Shadow Plate": [
        "armor",
        "anyarmor"
    ],
    "Sacred Armor": [
        "armor",
        "anyarmor"
    ],
    "Archon Plate": [
        "armor",
        "anyarmor"
    ],
    "Heater": [
        "shield",
        "anyshield"
    ],
    "Luna": [
        "shield",
        "anyshield"
    ],
    "Hyperion": [
        "shield",
        "anyshield"
    ],
    "Monarch": [
        "shield",
        "anyshield"
    ],
    "Aegis": [
        "shield",
        "anyshield"
    ],
    "Ward": [
        "shield",
        "anyshield"
    ],
    "Bramble Mitts": [
        "gloves",
        "anyarmor"
    ],
    "Vampirebone Gloves": [
        "gloves",
        "anyarmor"
    ],
    "Vambraces": [
        "gloves",
        "anyarmor"
    ],
    "Crusader Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "Ogre Gauntlets": [
        "gloves",
        "anyarmor"
    ],
    "Wyrmhide Boots": [
        "boots",
        "anyarmor"
    ],
    "Scarabshell Boots": [
        "boots",
        "anyarmor"
    ],
    "Boneweave Boots": [
        "boots",
        "anyarmor"
    ],
    "Mirrored Boots": [
        "boots",
        "anyarmor"
    ],
    "Myrmidon Greaves": [
        "boots",
        "anyarmor"
    ],
    "Spiderweb Sash": [
        "belt",
        "anyarmor"
    ],
    "Vampirefang Belt": [
        "belt",
        "anyarmor"
    ],
    "Mithril Coil": [
        "belt",
        "anyarmor"
    ],
    "Troll Belt": [
        "belt",
        "anyarmor"
    ],
    "Colossus Girdle": [
        "belt",
        "anyarmor"
    ],
    "Bone Visage": [
        "helm",
        "anyarmor"
    ],
    "Troll Nest": [
        "shield",
        "anyshield"
    ],
    "Blade Barrier": [
        "shield",
        "anyshield"
    ],
    "Alpha Helm": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Griffon Headdress": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Hunter's Guise": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Sacred Feathers": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Totemic Mask": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Jawbone Visor": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Lion Helm": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Rage Mask": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Savage Helmet": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Slayer Guard": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Akaran Targe": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Akaran Rondache": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Protector Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Gilded Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Royal Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Mummified Trophy": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Fetish Trophy": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Sexton Trophy": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Cantor Trophy": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Hierophant Trophy": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Blood Spirit": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Sun Spirit": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Earth Spirit": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Sky Spirit": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Dream Spirit": [
        "pelt",
        "helm",
        "druiditem"
    ],
    "Carnage Helm": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Fury Visor": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Destroyer Helm": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Conqueror Crown": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Guardian Crown": [
        "primalhelm",
        "helm",
        "barbarianitem"
    ],
    "Sacred Targe": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Sacred Rondache": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Kurast Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Zakarum Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Vortex Shield": [
        "auricshields",
        "anyshield",
        "paladinitem"
    ],
    "Minion Skull": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Hellspawn Skull": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Overseer Skull": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Succubus Skull": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Bloodlord Skull": [
        "voodooheads",
        "anyshield",
        "necromanceritem"
    ],
    "Hand Axe": [
        "axe",
        "meleeweapon"
    ],
    "Axe": [
        "axe",
        "meleeweapon"
    ],
    "Double Axe": [
        "axe",
        "meleeweapon"
    ],
    "Military Pick": [
        "axe",
        "meleeweapon"
    ],
    "War Axe": [
        "axe",
        "meleeweapon"
    ],
    "Large Axe": [
        "axe",
        "meleeweapon"
    ],
    "Broad Axe": [
        "axe",
        "meleeweapon"
    ],
    "Battle Axe": [
        "axe",
        "meleeweapon"
    ],
    "Great Axe": [
        "axe",
        "meleeweapon"
    ],
    "Giant Axe": [
        "axe",
        "meleeweapon"
    ],
    "Wand": [
        "wand",
        "stavesandrods"
    ],
    "Yew Wand": [
        "wand",
        "stavesandrods"
    ],
    "Bone Wand": [
        "wand",
        "stavesandrods"
    ],
    "Grim Wand": [
        "wand",
        "stavesandrods"
    ],
    "Club": [
        "club",
        "blunt"
    ],
    "Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "Grand Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "War Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "Spiked Club": [
        "club",
        "blunt"
    ],
    "Mace": [
        "mace",
        "blunt"
    ],
    "Morning Star": [
        "mace",
        "blunt"
    ],
    "Flail": [
        "mace",
        "blunt"
    ],
    "War Hammer": [
        "hammer",
        "blunt"
    ],
    "Maul": [
        "hammer",
        "blunt"
    ],
    "Great Maul": [
        "hammer",
        "blunt"
    ],
    "Short Sword": [
        "sword",
        "swordsandknives"
    ],
    "Scimitar": [
        "sword",
        "swordsandknives"
    ],
    "Sabre": [
        "sword",
        "swordsandknives"
    ],
    "Falchion": [
        "sword",
        "swordsandknives"
    ],
    "Crystal Sword": [
        "sword",
        "swordsandknives"
    ],
    "Broad Sword": [
        "sword",
        "swordsandknives"
    ],
    "Long Sword": [
        "sword",
        "swordsandknives"
    ],
    "War Sword": [
        "sword",
        "swordsandknives"
    ],
    "Two-Handed Sword": [
        "sword",
        "swordsandknives"
    ],
    "Claymore": [
        "sword",
        "swordsandknives"
    ],
    "Giant Sword": [
        "sword",
        "swordsandknives"
    ],
    "Bastard Sword": [
        "sword",
        "swordsandknives"
    ],
    "Flamberge": [
        "sword",
        "swordsandknives"
    ],
    "Great Sword": [
        "sword",
        "swordsandknives"
    ],
    "Dagger": [
        "knife",
        "swordsandknives"
    ],
    "Dirk": [
        "knife",
        "swordsandknives"
    ],
    "Kris": [
        "knife",
        "swordsandknives"
    ],
    "Blade": [
        "knife",
        "swordsandknives"
    ],
    "Throwing Knife": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Throwing Axe": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "Balanced Knife": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Balanced Axe": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "Javelin": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Pilum": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Short Spear": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Glaive": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Throwing Spear": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Spear": [
        "spear",
        "spearsandpolearms"
    ],
    "Trident": [
        "spear",
        "spearsandpolearms"
    ],
    "Brandistock": [
        "spear",
        "spearsandpolearms"
    ],
    "Spetum": [
        "spear",
        "spearsandpolearms"
    ],
    "Pike": [
        "spear",
        "spearsandpolearms"
    ],
    "Bardiche": [
        "polearm",
        "spearsandpolearms"
    ],
    "Voulge": [
        "polearm",
        "spearsandpolearms"
    ],
    "Scythe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Poleaxe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Halberd": [
        "polearm",
        "spearsandpolearms"
    ],
    "War Scythe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Short Staff": [
        "staff",
        "stavesandrods"
    ],
    "Long Staff": [
        "staff",
        "stavesandrods"
    ],
    "Gnarled Staff": [
        "staff",
        "stavesandrods"
    ],
    "Battle Staff": [
        "staff",
        "stavesandrods"
    ],
    "War Staff": [
        "staff",
        "stavesandrods"
    ],
    "Short Bow": [
        "bow",
        "missileweapon"
    ],
    "Hunter's Bow": [
        "bow",
        "missileweapon"
    ],
    "Long Bow": [
        "bow",
        "missileweapon"
    ],
    "Composite Bow": [
        "bow",
        "missileweapon"
    ],
    "Short Battle Bow": [
        "bow",
        "missileweapon"
    ],
    "Long Battle Bow": [
        "bow",
        "missileweapon"
    ],
    "Short War Bow": [
        "bow",
        "missileweapon"
    ],
    "Long War Bow": [
        "bow",
        "missileweapon"
    ],
    "Light Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Heavy Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Repeating Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Rancid Gas Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Oil Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Choking Gas Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Exploding Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Strangling Gas Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Fulminating Potion": [
        "missilepotion",
        "thrownweapon"
    ],
    "Decoy Gidbinn": [
        "knife",
        "swordsandknives"
    ],
    "The Gidbinn": [
        "knife",
        "swordsandknives"
    ],
    "Wirt's Leg": [
        "club",
        "blunt"
    ],
    "Horadric Malus": [
        "hammer",
        "blunt"
    ],
    "Hell Forge Hammer": [
        "hammer",
        "blunt"
    ],
    "Horadric Staff": [
        "staff",
        "stavesandrods"
    ],
    "Shaft of the Horadric Staff": [
        "staff",
        "stavesandrods"
    ],
    "Hatchet": [
        "axe",
        "meleeweapon"
    ],
    "Cleaver": [
        "axe",
        "meleeweapon"
    ],
    "Twin Axe": [
        "axe",
        "meleeweapon"
    ],
    "Crowbill": [
        "axe",
        "meleeweapon"
    ],
    "Naga": [
        "axe",
        "meleeweapon"
    ],
    "Military Axe": [
        "axe",
        "meleeweapon"
    ],
    "Bearded Axe": [
        "axe",
        "meleeweapon"
    ],
    "Tabar": [
        "axe",
        "meleeweapon"
    ],
    "Gothic Axe": [
        "axe",
        "meleeweapon"
    ],
    "Ancient Axe": [
        "axe",
        "meleeweapon"
    ],
    "Burnt Wand": [
        "wand",
        "stavesandrods"
    ],
    "Petrified Wand": [
        "wand",
        "stavesandrods"
    ],
    "Tomb Wand": [
        "wand",
        "stavesandrods"
    ],
    "Grave Wand": [
        "wand",
        "stavesandrods"
    ],
    "Cudgel": [
        "club",
        "blunt"
    ],
    "Rune Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "Holy Water Sprinkler": [
        "scepter",
        "stavesandrods"
    ],
    "Divine Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "Barbed Club": [
        "club",
        "blunt"
    ],
    "Flanged Mace": [
        "mace",
        "blunt"
    ],
    "Jagged Star": [
        "mace",
        "blunt"
    ],
    "Knout": [
        "mace",
        "blunt"
    ],
    "Battle Hammer": [
        "hammer",
        "blunt"
    ],
    "War Club": [
        "hammer",
        "blunt"
    ],
    "Martel de Fer": [
        "hammer",
        "blunt"
    ],
    "Gladius": [
        "sword",
        "swordsandknives"
    ],
    "Cutlass": [
        "sword",
        "swordsandknives"
    ],
    "Shamshir": [
        "sword",
        "swordsandknives"
    ],
    "Tulwar": [
        "sword",
        "swordsandknives"
    ],
    "Dimensional Blade": [
        "sword",
        "swordsandknives"
    ],
    "Battle Sword": [
        "sword",
        "swordsandknives"
    ],
    "Rune Sword": [
        "sword",
        "swordsandknives"
    ],
    "Ancient Sword": [
        "sword",
        "swordsandknives"
    ],
    "Espandon": [
        "sword",
        "swordsandknives"
    ],
    "Dacian Falx": [
        "sword",
        "swordsandknives"
    ],
    "Tusk Sword": [
        "sword",
        "swordsandknives"
    ],
    "Gothic Sword": [
        "sword",
        "swordsandknives"
    ],
    "Zweihander": [
        "sword",
        "swordsandknives"
    ],
    "Executioner Sword": [
        "sword",
        "swordsandknives"
    ],
    "Poignard": [
        "knife",
        "swordsandknives"
    ],
    "Rondel": [
        "knife",
        "swordsandknives"
    ],
    "Cinquedeas": [
        "knife",
        "swordsandknives"
    ],
    "Stiletto": [
        "knife",
        "swordsandknives"
    ],
    "Battle Dart": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Francisca": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "War Dart": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Hurlbat": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "War Javelin": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Great Pilum": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Simbilan": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Spiculum": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Harpoon": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "War Spear": [
        "spear",
        "spearsandpolearms"
    ],
    "Fuscina": [
        "spear",
        "spearsandpolearms"
    ],
    "War Fork": [
        "spear",
        "spearsandpolearms"
    ],
    "Yari": [
        "spear",
        "spearsandpolearms"
    ],
    "Lance": [
        "spear",
        "spearsandpolearms"
    ],
    "Lochaber Axe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Bill": [
        "polearm",
        "spearsandpolearms"
    ],
    "Battle Scythe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Partizan": [
        "polearm",
        "spearsandpolearms"
    ],
    "Bec-de-Corbin": [
        "polearm",
        "spearsandpolearms"
    ],
    "Grim Scythe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Jo Staff": [
        "staff",
        "stavesandrods"
    ],
    "Quarterstaff": [
        "staff",
        "stavesandrods"
    ],
    "Cedar Staff": [
        "staff",
        "stavesandrods"
    ],
    "Gothic Staff": [
        "staff",
        "stavesandrods"
    ],
    "Rune Staff": [
        "staff",
        "stavesandrods"
    ],
    "Edge Bow": [
        "bow",
        "missileweapon"
    ],
    "Razor Bow": [
        "bow",
        "missileweapon"
    ],
    "Cedar Bow": [
        "bow",
        "missileweapon"
    ],
    "Double Bow": [
        "bow",
        "missileweapon"
    ],
    "Short Siege Bow": [
        "bow",
        "missileweapon"
    ],
    "Large Siege Bow": [
        "bow",
        "missileweapon"
    ],
    "Rune Bow": [
        "bow",
        "missileweapon"
    ],
    "Gothic Bow": [
        "bow",
        "missileweapon"
    ],
    "Arbalest": [
        "crossbow",
        "missileweapon"
    ],
    "Siege Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Ballista": [
        "crossbow",
        "missileweapon"
    ],
    "Chu-Ko-Nu": [
        "crossbow",
        "missileweapon"
    ],
    "Khalim's Flail": [
        "mace",
        "blunt"
    ],
    "Khalim's Will": [
        "mace",
        "blunt"
    ],
    "Katar": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Wrist Blade": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Hatchet Hands": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Cestus": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Claws": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Blade Talons": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Scissors Katar": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Quhab": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Wrist Spike": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Fascia": [
        "handtohand",
        "meleeweapon",
        "assassinitem",
        "assassinclaw"
    ],
    "Hand Scythe": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Greater Claws": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Greater Talons": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Scissors Quhab": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Suwayyah": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Wrist Sword": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "War Fist": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Battle Cestus": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Feral Claws": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Runic Talons": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Scissors Suwayyah": [
        "assassinclaw",
        "handtohand",
        "assassinitem"
    ],
    "Tomahawk": [
        "axe",
        "meleeweapon"
    ],
    "Small Crescent": [
        "axe",
        "meleeweapon"
    ],
    "Ettin Axe": [
        "axe",
        "meleeweapon"
    ],
    "War Spike": [
        "axe",
        "meleeweapon"
    ],
    "Berserker Axe": [
        "axe",
        "meleeweapon"
    ],
    "Feral Axe": [
        "axe",
        "meleeweapon"
    ],
    "Silver-edged Axe": [
        "axe",
        "meleeweapon"
    ],
    "Decapitator": [
        "axe",
        "meleeweapon"
    ],
    "Champion Axe": [
        "axe",
        "meleeweapon"
    ],
    "Glorious Axe": [
        "axe",
        "meleeweapon"
    ],
    "Polished Wand": [
        "wand",
        "stavesandrods"
    ],
    "Ghost Wand": [
        "wand",
        "stavesandrods"
    ],
    "Lich Wand": [
        "wand",
        "stavesandrods"
    ],
    "Unearthed Wand": [
        "wand",
        "stavesandrods"
    ],
    "Truncheon": [
        "club",
        "blunt"
    ],
    "Mighty Scepter": [
        "scepter",
        "stavesandrods"
    ],
    "Seraph Rod": [
        "scepter",
        "stavesandrods"
    ],
    "Caduceus": [
        "scepter",
        "stavesandrods"
    ],
    "Tyrant Club": [
        "club",
        "blunt"
    ],
    "Reinforced Mace": [
        "mace",
        "blunt"
    ],
    "Devil Star": [
        "mace",
        "blunt"
    ],
    "Scourge": [
        "mace",
        "blunt"
    ],
    "Legendary Mallet": [
        "hammer",
        "blunt"
    ],
    "Ogre Maul": [
        "hammer",
        "blunt"
    ],
    "Thunder Maul": [
        "hammer",
        "blunt"
    ],
    "Falcata": [
        "sword",
        "swordsandknives"
    ],
    "Ataghan": [
        "sword",
        "swordsandknives"
    ],
    "Elegant Blade": [
        "sword",
        "swordsandknives"
    ],
    "Hydra Edge": [
        "sword",
        "swordsandknives"
    ],
    "Phase Blade": [
        "sword",
        "swordsandknives"
    ],
    "Conquest Sword": [
        "sword",
        "swordsandknives"
    ],
    "Cryptic Sword": [
        "sword",
        "swordsandknives"
    ],
    "Mythical Sword": [
        "sword",
        "swordsandknives"
    ],
    "Legend Sword": [
        "sword",
        "swordsandknives"
    ],
    "Highland Blade": [
        "sword",
        "swordsandknives"
    ],
    "Balrog Blade": [
        "sword",
        "swordsandknives"
    ],
    "Champion Sword": [
        "sword",
        "swordsandknives"
    ],
    "Colossus Sword": [
        "sword",
        "swordsandknives"
    ],
    "Colossus Blade": [
        "sword",
        "swordsandknives"
    ],
    "Bone Knife": [
        "knife",
        "swordsandknives"
    ],
    "Mithril Point": [
        "knife",
        "swordsandknives"
    ],
    "Fanged Knife": [
        "knife",
        "swordsandknives"
    ],
    "Legend Spike": [
        "knife",
        "swordsandknives"
    ],
    "Flying Knife": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Flying Axe": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "Winged Knife": [
        "throwingknife",
        "comboweapon",
        "knife"
    ],
    "Winged Axe": [
        "throwingaxe",
        "comboweapon",
        "axe"
    ],
    "Hyperion Javelin": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Stygian Pilum": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Balrog Spear": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Ghost Glaive": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Winged Harpoon": [
        "javelin",
        "comboweapon",
        "spear"
    ],
    "Hyperion Spear": [
        "spear",
        "spearsandpolearms"
    ],
    "Stygian Pike": [
        "spear",
        "spearsandpolearms"
    ],
    "Mancatcher": [
        "spear",
        "spearsandpolearms"
    ],
    "Ghost Spear": [
        "spear",
        "spearsandpolearms"
    ],
    "War Pike": [
        "spear",
        "spearsandpolearms"
    ],
    "Ogre Axe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Colossus Voulge": [
        "polearm",
        "spearsandpolearms"
    ],
    "Thresher": [
        "polearm",
        "spearsandpolearms"
    ],
    "Cryptic Axe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Great Poleaxe": [
        "polearm",
        "spearsandpolearms"
    ],
    "Giant Thresher": [
        "polearm",
        "spearsandpolearms"
    ],
    "Walking Stick": [
        "staff",
        "stavesandrods"
    ],
    "Stalagmite": [
        "staff",
        "stavesandrods"
    ],
    "Elder Staff": [
        "staff",
        "stavesandrods"
    ],
    "Shillelagh": [
        "staff",
        "stavesandrods"
    ],
    "Archon Staff": [
        "staff",
        "stavesandrods"
    ],
    "Spider Bow": [
        "bow",
        "missileweapon"
    ],
    "Blade Bow": [
        "bow",
        "missileweapon"
    ],
    "Shadow Bow": [
        "bow",
        "missileweapon"
    ],
    "Great Bow": [
        "bow",
        "missileweapon"
    ],
    "Diamond Bow": [
        "bow",
        "missileweapon"
    ],
    "Crusader Bow": [
        "bow",
        "missileweapon"
    ],
    "Ward Bow": [
        "bow",
        "missileweapon"
    ],
    "Hydra Bow": [
        "bow",
        "missileweapon"
    ],
    "Pellet Bow": [
        "crossbow",
        "missileweapon"
    ],
    "Gorgon Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Colossus Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Demon Crossbow": [
        "crossbow",
        "missileweapon"
    ],
    "Eagle Orb": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Sacred Globe": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Smoked Sphere": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Clasped Orb": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Jared's Stone": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Stag Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Reflex Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Maiden Spear": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Maiden Pike": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Maiden Javelin": [
        "amazonjavelin",
        "javelin",
        "amazonitem"
    ],
    "Glowing Orb": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Crystalline Globe": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Cloudy Sphere": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Sparkling Ball": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Swirling Crystal": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Ashwood Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Ceremonial Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Ceremonial Spear": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Ceremonial Pike": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Ceremonial Javelin": [
        "amazonjavelin",
        "javelin",
        "amazonitem"
    ],
    "Heavenly Stone": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Eldritch Orb": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Demon Heart": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Vortex Orb": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Dimensional Shard": [
        "orb",
        "weapon",
        "sorceressitem"
    ],
    "Matriarchal Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Grand Matron Bow": [
        "amazonbow",
        "bow",
        "amazonitem"
    ],
    "Matriarchal Spear": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Matriarchal Pike": [
        "amazonspear",
        "spear",
        "amazonitem"
    ],
    "Matriarchal Javelin": [
        "amazonjavelin",
        "javelin",
        "amazonitem"
    ],
    "Elixir": [
        "elixir",
        "miscellaneous"
    ],
    "null": [
        "manapotion",
        "potion"
    ],
    "Stamina Potion": [
        "staminapotion",
        "potion"
    ],
    "Antidote Potion": [
        "antidotepotion",
        "potion"
    ],
    "Rejuvenation Potion": [
        "rejuvpotion",
        "healingpotion",
        "manapotion"
    ],
    "Full Rejuvenation Potion": [
        "rejuvpotion",
        "healingpotion",
        "manapotion"
    ],
    "Thawing Potion": [
        "thawingpotion",
        "potion"
    ],
    "Tome of Town Portal": [
        "book",
        "miscellaneous"
    ],
    "Tome of Identify": [
        "book",
        "miscellaneous"
    ],
    "Amulet": [
        "amulet",
        "miscellaneous"
    ],
    "Top of the Horadric Staff": [
        "amulet",
        "miscellaneous"
    ],
    "Ring": [
        "ring",
        "miscellaneous"
    ],
    "Gold": [
        "gold",
        "miscellaneous"
    ],
    "Scroll of Inifuss": [
        "quest"
    ],
    "Key to the Cairn Stones": [
        "quest"
    ],
    "Arrows": [
        "bowquiver",
        "missile",
        "secondhand"
    ],
    "Torch": [
        "torch",
        "miscellaneous"
    ],
    "Bolts": [
        "crossbowquiver",
        "missile",
        "secondhand"
    ],
    "Scroll of Town Portal": [
        "scroll",
        "miscellaneous"
    ],
    "Scroll of Identify": [
        "scroll",
        "miscellaneous"
    ],
    "Heart": [
        "bodypart",
        "miscellaneous"
    ],
    "Brain": [
        "bodypart",
        "miscellaneous"
    ],
    "Jawbone": [
        "bodypart",
        "miscellaneous"
    ],
    "Eye": [
        "bodypart",
        "miscellaneous"
    ],
    "Horn": [
        "bodypart",
        "miscellaneous"
    ],
    "Tail": [
        "bodypart",
        "miscellaneous"
    ],
    "Flag": [
        "bodypart",
        "miscellaneous"
    ],
    "Fang": [
        "bodypart",
        "miscellaneous"
    ],
    "Quill": [
        "bodypart",
        "miscellaneous"
    ],
    "Soul": [
        "bodypart",
        "miscellaneous"
    ],
    "Scalp": [
        "bodypart",
        "miscellaneous"
    ],
    "Spleen": [
        "bodypart",
        "miscellaneous"
    ],
    "Key": [
        "key",
        "miscellaneous"
    ],
    "The Black Tower Key": [
        "key",
        "miscellaneous"
    ],
    "Potion of Life": [
        "quest"
    ],
    "A Jade Figurine": [
        "quest"
    ],
    "The Golden Bird": [
        "quest"
    ],
    "Lam Esen's Tome": [
        "quest"
    ],
    "Horadric Cube": [
        "quest"
    ],
    "Horadric Scroll": [
        "quest"
    ],
    "Mephisto's Soulstone": [
        "quest"
    ],
    "Book of Skill": [
        "quest"
    ],
    "Khalim's Eye": [
        "quest"
    ],
    "Khalim's Heart": [
        "quest"
    ],
    "Khalim's Brain": [
        "quest"
    ],
    "Ear": [
        "playerbodypart",
        "miscellaneous"
    ],
    "Chipped Amethyst": [
        "amethyst",
        "gem"
    ],
    "Flawed Amethyst": [
        "amethyst",
        "gem"
    ],
    "Amethyst": [
        "amethyst",
        "gem"
    ],
    "Flawless Amethyst": [
        "amethyst",
        "gem"
    ],
    "Perfect Amethyst": [
        "amethyst",
        "gem"
    ],
    "Chipped Topaz": [
        "topaz",
        "gem"
    ],
    "Flawed Topaz": [
        "topaz",
        "gem"
    ],
    "Topaz": [
        "topaz",
        "gem"
    ],
    "Flawless Topaz": [
        "topaz",
        "gem"
    ],
    "Perfect Topaz": [
        "topaz",
        "gem"
    ],
    "Chipped Sapphire": [
        "sapphire",
        "gem"
    ],
    "Flawed Sapphire": [
        "sapphire",
        "gem"
    ],
    "Sapphire": [
        "sapphire",
        "gem"
    ],
    "Flawless Sapphire": [
        "sapphire",
        "gem"
    ],
    "Perfect Sapphire": [
        "sapphire",
        "gem"
    ],
    "Chipped Emerald": [
        "emerald",
        "gem"
    ],
    "Flawed Emerald": [
        "emerald",
        "gem"
    ],
    "Emerald": [
        "emerald",
        "gem"
    ],
    "Flawless Emerald": [
        "emerald",
        "gem"
    ],
    "Perfect Emerald": [
        "emerald",
        "gem"
    ],
    "Chipped Ruby": [
        "ruby",
        "gem"
    ],
    "Flawed Ruby": [
        "ruby",
        "gem"
    ],
    "Ruby": [
        "ruby",
        "gem"
    ],
    "Flawless Ruby": [
        "ruby",
        "gem"
    ],
    "Perfect Ruby": [
        "ruby",
        "gem"
    ],
    "Chipped Diamond": [
        "diamond",
        "gem"
    ],
    "Flawed Diamond": [
        "diamond",
        "gem"
    ],
    "Diamond": [
        "diamond",
        "gem"
    ],
    "Flawless Diamond": [
        "diamond",
        "gem"
    ],
    "Perfect Diamond": [
        "diamond",
        "gem"
    ],
    "Minor Healing Potion": [
        "healingpotion",
        "potion"
    ],
    "Light Healing Potion": [
        "healingpotion",
        "potion"
    ],
    "Healing Potion": [
        "healingpotion",
        "potion"
    ],
    "Greater Healing Potion": [
        "healingpotion",
        "potion"
    ],
    "Super Healing Potion": [
        "healingpotion",
        "potion"
    ],
    "Minor Mana Potion": [
        "manapotion",
        "potion"
    ],
    "Light Mana Potion": [
        "manapotion",
        "potion"
    ],
    "Mana Potion": [
        "manapotion",
        "potion"
    ],
    "Greater Mana Potion": [
        "manapotion",
        "potion"
    ],
    "Super Mana Potion": [
        "manapotion",
        "potion"
    ],
    "Chipped Skull": [
        "skull",
        "gem"
    ],
    "Flawed Skull": [
        "skull",
        "gem"
    ],
    "Skull": [
        "skull",
        "gem"
    ],
    "Flawless Skull": [
        "skull",
        "gem"
    ],
    "Perfect Skull": [
        "skull",
        "gem"
    ],
    "Herb": [
        "herb",
        "miscellaneous"
    ],
    "Small Charm": [
        "smallcharm",
        "charm"
    ],
    "Large Charm": [
        "mediumcharm",
        "charm"
    ],
    "Grand Charm": [
        "largecharm",
        "charm"
    ],
    "El Rune": [
        "rune",
        "socketfiller"
    ],
    "Eld Rune": [
        "rune",
        "socketfiller"
    ],
    "Tir Rune": [
        "rune",
        "socketfiller"
    ],
    "Nef Rune": [
        "rune",
        "socketfiller"
    ],
    "Eth Rune": [
        "rune",
        "socketfiller"
    ],
    "Ith Rune": [
        "rune",
        "socketfiller"
    ],
    "Tal Rune": [
        "rune",
        "socketfiller"
    ],
    "Ral Rune": [
        "rune",
        "socketfiller"
    ],
    "Ort Rune": [
        "rune",
        "socketfiller"
    ],
    "Thul Rune": [
        "rune",
        "socketfiller"
    ],
    "Amn Rune": [
        "rune",
        "socketfiller"
    ],
    "Sol Rune": [
        "rune",
        "socketfiller"
    ],
    "Shael Rune": [
        "rune",
        "socketfiller"
    ],
    "Dol Rune": [
        "rune",
        "socketfiller"
    ],
    "Hel Rune": [
        "rune",
        "socketfiller"
    ],
    "Io Rune": [
        "rune",
        "socketfiller"
    ],
    "Lum Rune": [
        "rune",
        "socketfiller"
    ],
    "Ko Rune": [
        "rune",
        "socketfiller"
    ],
    "Fal Rune": [
        "rune",
        "socketfiller"
    ],
    "Lem Rune": [
        "rune",
        "socketfiller"
    ],
    "Pul Rune": [
        "rune",
        "socketfiller"
    ],
    "Um Rune": [
        "rune",
        "socketfiller"
    ],
    "Mal Rune": [
        "rune",
        "socketfiller"
    ],
    "Ist Rune": [
        "rune",
        "socketfiller"
    ],
    "Gul Rune": [
        "rune",
        "socketfiller"
    ],
    "Vex Rune": [
        "rune",
        "socketfiller"
    ],
    "Ohm Rune": [
        "rune",
        "socketfiller"
    ],
    "Lo Rune": [
        "rune",
        "socketfiller"
    ],
    "Sur Rune": [
        "rune",
        "socketfiller"
    ],
    "Ber Rune": [
        "rune",
        "socketfiller"
    ],
    "Jah Rune": [
        "rune",
        "socketfiller"
    ],
    "Cham Rune": [
        "rune",
        "socketfiller"
    ],
    "Zod Rune": [
        "rune",
        "socketfiller"
    ],
    "Jewel": [
        "jewel",
        "socketfiller"
    ],
    "Malah's Potion": [
        "quest"
    ],
    "Scroll of Knowledge": [
        "scroll",
        "miscellaneous"
    ],
    "Scroll of Resistance": [
        "quest"
    ],
    "Key of Terror": [
        "quest"
    ],
    "Key of Hate": [
        "quest"
    ],
    "Key of Destruction": [
        "quest"
    ],
    "Diablo's Horn": [
        "quest"
    ],
    "Baal's Eye": [
        "quest"
    ],
    "Mephisto's Brain": [
        "quest"
    ],
    "Token of Absolution": [
        "quest"
    ],
    "Twisted Essence of Suffering": [
        "quest"
    ],
    "Charged Essence of Hatred": [
        "quest"
    ],
    "Burning Essence of Terror": [
        "quest"
    ],
    "Festering Essence of Destruction": [
        "quest"
    ],
    "Standard of Heroes": [
        "quest"
    ]
}