from d2r_image.data_models import ItemQuality, ItemQualityKeyword


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
    "Defense: {}": [
        "31"
    ],
    "+{} Defense vs. Missile": [
        "32"
    ],
    "+{} Defense vs. Melee": [
        "33"
    ],
    "Damage Reduced by {}": [
        "34"
    ],
    "Damage Reduced by {}%": [
        "36"
    ],
    "+{}% Enhanced Defense": [
        "16"
    ],
    "Magic Damage Reduced by {}": [
        "35"
    ],
    "+{} to Strength": [
        "0"
    ],
    "+{} to Dexterity": [
        "2"
    ],
    "+{} to Vitality": [
        "3"
    ],
    "+{} to Energy": [
        "1"
    ],
    "+{} to Mana": [
        "9"
    ],
    "Increase Maximum Mana {}%": [
        "77"
    ],
    "+{} to Life": [
        "7"
    ],
    "Increase Maximum Life {}%": [
        "76"
    ],
    "+{} to Attack Rating": [
        "19"
    ],
    "{}% Increased Chance of Blocking": [
        "20"
    ],
    "+{} to Minimum Cold Damage": [
        "54"
    ],
    "+{} to Maximum Cold Damage": [
        "55"
    ],
    "+{} to Minimum Fire Damage": [
        "48"
    ],
    "+{} to Maximum Fire Damage": [
        "49"
    ],
    "+{} to Minimum Lightning Damage": [
        "50"
    ],
    "+{} to Maximum Lightning Damage": [
        "51"
    ],
    "+{} to Minimum Poison Damage": [
        "57"
    ],
    "+{} to Maximum Poison Damage": [
        "58"
    ],
    "{}% Damage Taken Goes To Mana": [
        "114"
    ],
    "Fire Resist +{}%": [
        "39"
    ],
    "+{}% to Maximum Fire Resist": [
        "40"
    ],
    "Lightning Resist +{}%": [
        "41"
    ],
    "+{}% to Maximum Lightning Resist": [
        "42"
    ],
    "Cold Resist +{}%": [
        "43"
    ],
    "+{}% to Maximum Cold Resist": [
        "44"
    ],
    "Magic Resist +{}%": [
        "37"
    ],
    "+{}% to Maximum Magic Resist": [
        "38"
    ],
    "Poison Resist +{}%": [
        "45"
    ],
    "+{}% to Maximum Poison Resist": [
        "46"
    ],
    "All Resistances +{}": [
        "6969",
        "39",
        "41",
        "43",
        "45"
    ],
    "+{} Fire Absorb": [
        "142"
    ],
    "Fire Absorb {}%": [
        "143"
    ],
    "+{} Lightning Absorb": [
        "144"
    ],
    "Lightning Absorb {}%": [
        "145"
    ],
    "+{} Magic Absorb": [
        "146"
    ],
    "Magic Absorb {}%": [
        "147"
    ],
    "+{} Cold Absorb": [
        "148"
    ],
    "Cold Absorb {}%": [
        "149"
    ],
    "Durability: {} of {}": [
        "72",
        "73"
    ],
    "Increase Maximum Durability {}%": [
        "75"
    ],
    "Replenish Life +{}": [
        "74"
    ],
    "Attacker Takes Damage of {}": [
        "78"
    ],
    "+{}% Increased Attack Speed": [
        "93"
    ],
    "{}% Extra Gold from Monsters": [
        "79"
    ],
    "{}% Better Chance of Getting Magic Items": [
        "80"
    ],
    "Knockback": [
        "81"
    ],
    "Heal Stamina Plus {}%": [
        "28"
    ],
    "Regenerate Mana {}%": [
        "27"
    ],
    "+{} Maximum Stamina": [
        "11"
    ],
    "{}% Mana stolen per hit": [
        "62"
    ],
    "{}% Life stolen per hit": [
        "60"
    ],
    "+{} to Amazon Skill Levels": [
        "83,0"
    ],
    "+{} to Paladin Skill Levels": [
        "83,3"
    ],
    "+{} to Necromancer Skill Levels": [
        "83,2"
    ],
    "+{} to Sorceress Skill Levels": [
        "83,1"
    ],
    "+{} to Barbarian Skill Levels": [
        "83,4"
    ],
    "+{} to Light Radius": [
        "89"
    ],
    "Requirements -{}%": [
        "91"
    ],
    "+{}% Faster Run/Walk": [
        "96"
    ],
    "+{}% Faster Hit Recovery": [
        "99"
    ],
    "+{}% Faster Block Rate": [
        "102"
    ],
    "+{}% Faster Cast Rate": [
        "105"
    ],
    "Poison Length Reduced by {}%": [
        "110"
    ],
    "Damage +{}": [
        "111"
    ],
    "Hit Causes Monster to Flee {}%": [
        "112"
    ],
    "Hit Blinds Target +{}": [
        "113"
    ],
    "Ignore Target's Defense": [
        "115"
    ],
    "-{}% Target Defense": [
        "116"
    ],
    "Prevent Monster Heal": [
        "117"
    ],
    "Half Freeze Duration": [
        "118"
    ],
    "{}% Bonus to Attack Rating": [
        "119"
    ],
    "-{} to Monster Defense Per Hit": [
        "120"
    ],
    "+{}% Damage to Demons": [
        "121"
    ],
    "+{}% Damage to Undead": [
        "122"
    ],
    "+{} to Attack Rating against Demons": [
        "123"
    ],
    "+{} to Attack Rating against Undead": [
        "124"
    ],
    "+{} to Fire Skills": [
        "126"
    ],
    "+{} to All Skills": [
        "127"
    ],
    "Attacker Takes Lightning Damage of {}": [
        "128"
    ],
    "Freezes Target +{}": [
        "134"
    ],
    "{}% Chance of Open Wounds": [
        "135"
    ],
    "{}% Chance of Crushing Blow": [
        "136"
    ],
    "+{} Kick Damage": [
        "137"
    ],
    "+{} to Mana after each Kill": [
        "138"
    ],
    "+{} Life after each Demon Kill": [
        "139"
    ],
    "{}% Deadly Strike": [
        "141"
    ],
    "Slows Target by {}%": [
        "150"
    ],
    "Cannot Be Frozen": [
        "153"
    ],
    "{}% Slower Stamina Drain": [
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
    "+{} to Druid Skill Levels": [
        "83,5"
    ],
    "+{} to Assassin Skill Levels": [
        "83,6"
    ],
    "+{} to Magic Arrow (Amazon only)": [
        "107,6"
    ],
    "+{} to Fire Arrow (Amazon only)": [
        "107,7"
    ],
    "+{} to Inner Sight (Amazon only)": [
        "107,8"
    ],
    "+{} to Critical Strike (Amazon only)": [
        "107,9"
    ],
    "+{} to Jab (Amazon only)": [
        "107,10"
    ],
    "+{} to Cold Arrow (Amazon only)": [
        "107,11"
    ],
    "+{} to Multiple Shot (Amazon only)": [
        "107,12"
    ],
    "+{} to Dodge (Amazon only)": [
        "107,13"
    ],
    "+{} to Power Strike (Amazon only)": [
        "107,14"
    ],
    "+{} to Poison Javelin (Amazon only)": [
        "107,15"
    ],
    "+{} to Exploding Arrow (Amazon only)": [
        "107,16"
    ],
    "+{} to Slow Missiles (Amazon only)": [
        "107,17"
    ],
    "+{} to Avoid (Amazon only)": [
        "107,18"
    ],
    "+{} to Impale (Amazon only)": [
        "107,19"
    ],
    "+{} to Lightning Bolt (Amazon only)": [
        "107,20"
    ],
    "+{} to Ice Arrow (Amazon only)": [
        "107,21"
    ],
    "+{} to Guided Arrow (Amazon only)": [
        "107,22"
    ],
    "+{} to Penetrate (Amazon only)": [
        "107,23"
    ],
    "+{} to Charged Strike (Amazon only)": [
        "107,24"
    ],
    "+{} to Plague Javelin (Amazon only)": [
        "107,25"
    ],
    "+{} to Strafe (Amazon only)": [
        "107,26"
    ],
    "+{} to Immolation Arrow (Amazon only)": [
        "107,27"
    ],
    "+{} to Decoy (Amazon only)": [
        "107,28"
    ],
    "+{} to Evade (Amazon only)": [
        "107,29"
    ],
    "+{} to Fend (Amazon only)": [
        "107,30"
    ],
    "+{} to Freezing Arrow (Amazon only)": [
        "107,31"
    ],
    "+{} to Valkyrie (Amazon only)": [
        "107,32"
    ],
    "+{} to Pierce (Amazon only)": [
        "107,33"
    ],
    "+{} to Lightning Strike (Amazon only)": [
        "107,34"
    ],
    "+{} to Lightning Fury (Amazon only)": [
        "107,35"
    ],
    "+{} to Fire Bolt (Sorceress only)": [
        "107,36"
    ],
    "+{} to Warmth (Sorceress only)": [
        "107,37"
    ],
    "+{} to Charged Bolt (Sorceress only)": [
        "107,38"
    ],
    "+{} to Ice Bolt (Sorceress only)": [
        "107,39"
    ],
    "+{} to Frozen Armor (Sorceress only)": [
        "107,40"
    ],
    "+{} to Inferno (Sorceress only)": [
        "107,41"
    ],
    "+{} to Static Field (Sorceress only)": [
        "107,42"
    ],
    "+{} to Telekinesis (Sorceress only)": [
        "107,43"
    ],
    "+{} to Frost Nova (Sorceress only)": [
        "107,44"
    ],
    "+{} to Ice Blast (Sorceress only)": [
        "107,45"
    ],
    "+{} to Blaze (Sorceress only)": [
        "107,46"
    ],
    "+{} to Fire Ball (Sorceress only)": [
        "107,47"
    ],
    "+{} to Nova (Sorceress only)": [
        "107,48"
    ],
    "+{} to Lightning (Sorceress only)": [
        "107,49"
    ],
    "+{} to Shiver Armor (Sorceress only)": [
        "107,50"
    ],
    "+{} to Fire Wall (Sorceress only)": [
        "107,51"
    ],
    "+{} to Enchant (Sorceress only)": [
        "107,52"
    ],
    "+{} to Chain Lightning (Sorceress only)": [
        "107,53"
    ],
    "+{} to Teleport (Sorceress only)": [
        "107,54"
    ],
    "+{} to Glacial Spike (Sorceress only)": [
        "107,55"
    ],
    "+{} to Meteor (Sorceress only)": [
        "107,56"
    ],
    "+{} to Thunder Storm (Sorceress only)": [
        "107,57"
    ],
    "+{} to Energy Shield (Sorceress only)": [
        "107,58"
    ],
    "+{} to Blizzard (Sorceress only)": [
        "107,59"
    ],
    "+{} to Chilling Armor (Sorceress only)": [
        "107,60"
    ],
    "+{} to Fire Mastery (Sorceress only)": [
        "107,61"
    ],
    "+{} to Hydra (Sorceress only)": [
        "107,62"
    ],
    "+{} to Lightning Mastery (Sorceress only)": [
        "107,63"
    ],
    "+{} to Frozen Orb (Sorceress only)": [
        "107,64"
    ],
    "+{} to Cold Mastery (Sorceress only)": [
        "107,65"
    ],
    "+{} to Amplify Damage (Necromancer only)": [
        "107,66"
    ],
    "+{} to Teeth (Necromancer only)": [
        "107,67"
    ],
    "+{} to Bone Armor (Necromancer only)": [
        "107,68"
    ],
    "+{} to Skeleton Mastery (Necromancer only)": [
        "107,69"
    ],
    "+{} to Raise Skeleton (Necromancer only)": [
        "107,70"
    ],
    "+{} to Dim Vision (Necromancer only)": [
        "107,71"
    ],
    "+{} to Weaken (Necromancer only)": [
        "107,72"
    ],
    "+{} to Poison Dagger (Necromancer only)": [
        "107,73"
    ],
    "+{} to Corpse Explosion (Necromancer only)": [
        "107,74"
    ],
    "+{} to Clay Golem (Necromancer only)": [
        "107,75"
    ],
    "+{} to Iron Maiden (Necromancer only)": [
        "107,76"
    ],
    "+{} to Terror (Necromancer only)": [
        "107,77"
    ],
    "+{} to Bone Wall (Necromancer only)": [
        "107,78"
    ],
    "+{} to Golem Mastery (Necromancer only)": [
        "107,79"
    ],
    "+{} to Raise Skeletal Mage (Necromancer only)": [
        "107,80"
    ],
    "+{} to Confuse (Necromancer only)": [
        "107,81"
    ],
    "+{} to Life Tap (Necromancer only)": [
        "107,82"
    ],
    "+{} to Poison Explosion (Necromancer only)": [
        "107,83"
    ],
    "+{} to Bone Spear (Necromancer only)": [
        "107,84"
    ],
    "+{} to Blood Golem (Necromancer only)": [
        "107,85"
    ],
    "+{} to Attract (Necromancer only)": [
        "107,86"
    ],
    "+{} to Decrepify (Necromancer only)": [
        "107,87"
    ],
    "+{} to Bone Prison (Necromancer only)": [
        "107,88"
    ],
    "+{} to Summon Resist (Necromancer only)": [
        "107,89"
    ],
    "+{} to Iron Golem (Necromancer only)": [
        "107,90"
    ],
    "+{} to Lower Resist (Necromancer only)": [
        "107,91"
    ],
    "+{} to Poison Nova (Necromancer only)": [
        "107,92"
    ],
    "+{} to Bone Spirit (Necromancer only)": [
        "107,93"
    ],
    "+{} to Fire Golem (Necromancer only)": [
        "107,94"
    ],
    "+{} to Revive (Necromancer only)": [
        "107,95"
    ],
    "+{} to Sacrifice (Paladin only)": [
        "107,96"
    ],
    "+{} to Smite (Paladin only)": [
        "107,97"
    ],
    "+{} to Might (Paladin only)": [
        "107,98"
    ],
    "+{} to Prayer (Paladin only)": [
        "107,99"
    ],
    "+{} to Resist Fire (Paladin only)": [
        "107,100"
    ],
    "+{} to Holy Bolt (Paladin only)": [
        "107,101"
    ],
    "+{} to Holy Fire (Paladin only)": [
        "107,102"
    ],
    "+{} to Thorns (Paladin only)": [
        "107,103"
    ],
    "+{} to Defiance (Paladin only)": [
        "107,104"
    ],
    "+{} to Resist Cold (Paladin only)": [
        "107,105"
    ],
    "+{} to Zeal (Paladin only)": [
        "107,106"
    ],
    "+{} to Charge (Paladin only)": [
        "107,107"
    ],
    "+{} to Blessed Aim (Paladin only)": [
        "107,108"
    ],
    "+{} to Cleansing (Paladin only)": [
        "107,109"
    ],
    "+{} to Resist Lightning (Paladin only)": [
        "107,110"
    ],
    "+{} to Vengeance (Paladin only)": [
        "107,111"
    ],
    "+{} to Blessed Hammer (Paladin only)": [
        "107,112"
    ],
    "+{} to Concentration (Paladin only)": [
        "107,113"
    ],
    "+{} to Holy Freeze (Paladin only)": [
        "107,114"
    ],
    "+{} to Vigor (Paladin only)": [
        "107,115"
    ],
    "+{} to Conversion (Paladin only)": [
        "107,116"
    ],
    "+{} to Holy Shield (Paladin only)": [
        "107,117"
    ],
    "+{} to Holy Shock (Paladin only)": [
        "107,118"
    ],
    "+{} to Sanctuary (Paladin only)": [
        "107,119"
    ],
    "+{} to Meditation (Paladin only)": [
        "107,120"
    ],
    "+{} to Fist of the Heavens (Paladin only)": [
        "107,121"
    ],
    "+{} to Fanaticism (Paladin only)": [
        "107,122"
    ],
    "+{} to Conviction (Paladin only)": [
        "107,123"
    ],
    "+{} to Redemption (Paladin only)": [
        "107,124"
    ],
    "+{} to Salvation (Paladin only)": [
        "107,125"
    ],
    "+{} to Bash (Barbarian only)": [
        "107,126"
    ],
    "+{} to Blade Mastery (Barbarian only)": [
        "107,127"
    ],
    "+{} to Axe Mastery (Barbarian only)": [
        "107,128"
    ],
    "+{} to Mace Mastery (Barbarian only)": [
        "107,129"
    ],
    "+{} to Howl (Barbarian only)": [
        "107,130"
    ],
    "+{} to Find Potion (Barbarian only)": [
        "107,131"
    ],
    "+{} to Leap (Barbarian only)": [
        "107,132"
    ],
    "+{} to Double Swing (Barbarian only)": [
        "107,133"
    ],
    "+{} to Polearm Mastery (Barbarian only)": [
        "107,134"
    ],
    "+{} to Throwing Mastery (Barbarian only)": [
        "107,135"
    ],
    "+{} to Spear Mastery (Barbarian only)": [
        "107,136"
    ],
    "+{} to Taunt (Barbarian only)": [
        "107,137"
    ],
    "+{} to Shout (Barbarian only)": [
        "107,138"
    ],
    "+{} to Stun (Barbarian only)": [
        "107,139"
    ],
    "+{} to Double Throw (Barbarian only)": [
        "107,140"
    ],
    "+{} to Increased Stamina (Barbarian only)": [
        "107,141"
    ],
    "+{} to Find Item (Barbarian only)": [
        "107,142"
    ],
    "+{} to Leap Attack (Barbarian only)": [
        "107,143"
    ],
    "+{} to Concentrate (Barbarian only)": [
        "107,144"
    ],
    "+{} to Iron Skin (Barbarian only)": [
        "107,145"
    ],
    "+{} to Battle Cry (Barbarian only)": [
        "107,146"
    ],
    "+{} to Frenzy (Barbarian only)": [
        "107,147"
    ],
    "+{} to Increased Speed (Barbarian only)": [
        "107,148"
    ],
    "+{} to Battle Orders (Barbarian only)": [
        "107,149"
    ],
    "+{} to Grim Ward (Barbarian only)": [
        "107,150"
    ],
    "+{} to Whirlwind (Barbarian only)": [
        "107,151"
    ],
    "+{} to Berserk (Barbarian only)": [
        "107,152"
    ],
    "+{} to Natural Resistance (Barbarian only)": [
        "107,153"
    ],
    "+{} to War Cry (Barbarian only)": [
        "107,154"
    ],
    "+{} to Battle Command (Barbarian only)": [
        "107,155"
    ],
    "+{} to Raven (Druid only)": [
        "107,221"
    ],
    "+{} to Poison Creeper (Druid only)": [
        "107,222"
    ],
    "+{} to Werewolf (Druid only)": [
        "107,223"
    ],
    "+{} to Lycanthropy (Druid only)": [
        "107,224"
    ],
    "+{} to Firestorm (Druid only)": [
        "107,225"
    ],
    "+{} to Oak Sage (Druid only)": [
        "107,226"
    ],
    "+{} to Summon Spirit Wolf (Druid only)": [
        "107,227"
    ],
    "+{} to Werebear (Druid only)": [
        "107,228"
    ],
    "+{} to Molten Boulder (Druid only)": [
        "107,229"
    ],
    "+{} to Arctic Blast (Druid only)": [
        "107,230"
    ],
    "+{} to Carrion Vine (Druid only)": [
        "107,231"
    ],
    "+{} to Feral Rage (Druid only)": [
        "107,232"
    ],
    "+{} to Maul (Druid only)": [
        "107,233"
    ],
    "+{} to Fissure (Druid only)": [
        "107,234"
    ],
    "+{} to Cyclone Armor (Druid only)": [
        "107,235"
    ],
    "+{} to Heart of Wolverine (Druid only)": [
        "107,236"
    ],
    "+{} to Summon Dire Wolf (Druid only)": [
        "107,237"
    ],
    "+{} to Rabies (Druid only)": [
        "107,238"
    ],
    "+{} to Fire Claws (Druid only)": [
        "107,239"
    ],
    "+{} to Twister (Druid only)": [
        "107,240"
    ],
    "+{} to Solar Creeper (Druid only)": [
        "107,241"
    ],
    "+{} to Hunger (Druid only)": [
        "107,242"
    ],
    "+{} to Shock Wave (Druid only)": [
        "107,243"
    ],
    "+{} to Volcano (Druid only)": [
        "107,244"
    ],
    "+{} to Tornado (Druid only)": [
        "107,245"
    ],
    "+{} to Spirit of Barbs (Druid only)": [
        "107,246"
    ],
    "+{} to Summon Grizzly (Druid only)": [
        "107,247"
    ],
    "+{} to Fury (Druid only)": [
        "107,248"
    ],
    "+{} to Armageddon (Druid only)": [
        "107,249"
    ],
    "+{} to Hurricane (Druid only)": [
        "107,250"
    ],
    "+{} to Fire Blast (Assassin only)": [
        "107,251"
    ],
    "+{} to Claw Mastery (Assassin only)": [
        "107,252"
    ],
    "+{} to Psychic Hammer (Assassin only)": [
        "107,253"
    ],
    "+{} to Tiger Strike (Assassin only)": [
        "107,254"
    ],
    "+{} to Dragon Talon (Assassin only)": [
        "107,255"
    ],
    "+{} to Shock Web (Assassin only)": [
        "107,256"
    ],
    "+{} to Blade Sentinel (Assassin only)": [
        "107,257"
    ],
    "+{} to Burst of Speed (Assassin only)": [
        "107,258"
    ],
    "+{} to Fists of Fire (Assassin only)": [
        "107,259"
    ],
    "+{} to Dragon Claw (Assassin only)": [
        "107,260"
    ],
    "+{} to Charged Bolt Sentry (Assassin only)": [
        "107,261"
    ],
    "+{} to Wake of Fire (Assassin only)": [
        "107,262"
    ],
    "+{} to Weapon Block (Assassin only)": [
        "107,263"
    ],
    "+{} to Cloak of Shadows (Assassin only)": [
        "107,264"
    ],
    "+{} to Cobra Strike (Assassin only)": [
        "107,265"
    ],
    "+{} to Blade Fury (Assassin only)": [
        "107,266"
    ],
    "+{} to Fade (Assassin only)": [
        "107,267"
    ],
    "+{} to Shadow Warrior (Assassin only)": [
        "107,268"
    ],
    "+{} to Claws of Thunder (Assassin only)": [
        "107,269"
    ],
    "+{} to Dragon Tail (Assassin only)": [
        "107,270"
    ],
    "+{} to Lightning Sentry (Assassin only)": [
        "107,271"
    ],
    "+{} to Wake of Inferno (Assassin only)": [
        "107,272"
    ],
    "+{} to Mind Blast (Assassin only)": [
        "107,273"
    ],
    "+{} to Blades of Ice (Assassin only)": [
        "107,274"
    ],
    "+{} to Dragon Flight (Assassin only)": [
        "107,275"
    ],
    "+{} to Death Sentry (Assassin only)": [
        "107,276"
    ],
    "+{} to Blade Shield (Assassin only)": [
        "107,277"
    ],
    "+{} to Venom (Assassin only)": [
        "107,278"
    ],
    "+{} to Shadow Master (Assassin only)": [
        "107,279"
    ],
    "+{} to Phoenix Strike (Assassin only)": [
        "107,280"
    ],
    "{} to Bow and Crossbow Skills (Amazon Only)": [
        "188,0"
    ],
    "{} to Passive and Magic Skills (Amazon Only)": [
        "188,1"
    ],
    "{} to Javelin and Spear Skills (Amazon Only)": [
        "188,2"
    ],
    "{} to Fire Skills (Sorceress Only)": [
        "188,3"
    ],
    "{} to Lightning Skills (Sorceress Only)": [
        "188,4"
    ],
    "{} to Cold Skills (Sorceress Only)": [
        "188,5"
    ],
    "{} to Curses (Necromancer Only)": [
        "188,6"
    ],
    "{} to Poison and Bone Skills (Necromancer Only)": [
        "188,7"
    ],
    "{} to Combat Skills (Necromancer Only)": [
        "188,8"
    ],
    "{} to Combat Skills (Paladin Only)": [
        "188,9"
    ],
    "{} to Offensive Auras (Paladin Only)": [
        "188,10"
    ],
    "{} to Defensive Auras (Paladin Only)": [
        "188,11"
    ],
    "{} to Combat Skills (Barbarian Only)": [
        "188,12"
    ],
    "{} to Masteries (Barbarian Only)": [
        "188,13"
    ],
    "{} to Warcries (Barbarian Only)": [
        "188,14"
    ],
    "{} to Summoning Skills (Druid Only)": [
        "188,15"
    ],
    "{} to Shape Shifting Skills (Druid Only)": [
        "188,16"
    ],
    "{} to Elemental Skills (Druid Only)": [
        "188,17"
    ],
    "{} to Traps (Assassin Only)": [
        "188,18"
    ],
    "{} to Shadow Disciplines (Assassin Only)": [
        "188,19"
    ],
    "{} to Martial Arts (Assassin Only)": [
        "188,20"
    ],
    "Level {} Magic Arrow Aura When Equipped": [
        "151,6"
    ],
    "Level {} Fire Arrow Aura When Equipped": [
        "151,7"
    ],
    "Level {} Inner Sight Aura When Equipped": [
        "151,8"
    ],
    "Level {} Critical Strike Aura When Equipped": [
        "151,9"
    ],
    "Level {} Jab Aura When Equipped": [
        "151,10"
    ],
    "Level {} Cold Arrow Aura When Equipped": [
        "151,11"
    ],
    "Level {} Multiple Shot Aura When Equipped": [
        "151,12"
    ],
    "Level {} Dodge Aura When Equipped": [
        "151,13"
    ],
    "Level {} Power Strike Aura When Equipped": [
        "151,14"
    ],
    "Level {} Poison Javelin Aura When Equipped": [
        "151,15"
    ],
    "Level {} Exploding Arrow Aura When Equipped": [
        "151,16"
    ],
    "Level {} Slow Missiles Aura When Equipped": [
        "151,17"
    ],
    "Level {} Avoid Aura When Equipped": [
        "151,18"
    ],
    "Level {} Impale Aura When Equipped": [
        "151,19"
    ],
    "Level {} Lightning Bolt Aura When Equipped": [
        "151,20"
    ],
    "Level {} Ice Arrow Aura When Equipped": [
        "151,21"
    ],
    "Level {} Guided Arrow Aura When Equipped": [
        "151,22"
    ],
    "Level {} Penetrate Aura When Equipped": [
        "151,23"
    ],
    "Level {} Charged Strike Aura When Equipped": [
        "151,24"
    ],
    "Level {} Plague Javelin Aura When Equipped": [
        "151,25"
    ],
    "Level {} Strafe Aura When Equipped": [
        "151,26"
    ],
    "Level {} Immolation Arrow Aura When Equipped": [
        "151,27"
    ],
    "Level {} Decoy Aura When Equipped": [
        "151,28"
    ],
    "Level {} Evade Aura When Equipped": [
        "151,29"
    ],
    "Level {} Fend Aura When Equipped": [
        "151,30"
    ],
    "Level {} Freezing Arrow Aura When Equipped": [
        "151,31"
    ],
    "Level {} Valkyrie Aura When Equipped": [
        "151,32"
    ],
    "Level {} Pierce Aura When Equipped": [
        "151,33"
    ],
    "Level {} Lightning Strike Aura When Equipped": [
        "151,34"
    ],
    "Level {} Lightning Fury Aura When Equipped": [
        "151,35"
    ],
    "Level {} Fire Bolt Aura When Equipped": [
        "151,36"
    ],
    "Level {} Warmth Aura When Equipped": [
        "151,37"
    ],
    "Level {} Charged Bolt Aura When Equipped": [
        "151,38"
    ],
    "Level {} Ice Bolt Aura When Equipped": [
        "151,39"
    ],
    "Level {} Frozen Armor Aura When Equipped": [
        "151,40"
    ],
    "Level {} Inferno Aura When Equipped": [
        "151,41"
    ],
    "Level {} Static Field Aura When Equipped": [
        "151,42"
    ],
    "Level {} Telekinesis Aura When Equipped": [
        "151,43"
    ],
    "Level {} Frost Nova Aura When Equipped": [
        "151,44"
    ],
    "Level {} Ice Blast Aura When Equipped": [
        "151,45"
    ],
    "Level {} Blaze Aura When Equipped": [
        "151,46"
    ],
    "Level {} Fire Ball Aura When Equipped": [
        "151,47"
    ],
    "Level {} Nova Aura When Equipped": [
        "151,48"
    ],
    "Level {} Lightning Aura When Equipped": [
        "151,49"
    ],
    "Level {} Shiver Armor Aura When Equipped": [
        "151,50"
    ],
    "Level {} Fire Wall Aura When Equipped": [
        "151,51"
    ],
    "Level {} Enchant Aura When Equipped": [
        "151,52"
    ],
    "Level {} Chain Lightning Aura When Equipped": [
        "151,53"
    ],
    "Level {} Teleport Aura When Equipped": [
        "151,54"
    ],
    "Level {} Glacial Spike Aura When Equipped": [
        "151,55"
    ],
    "Level {} Meteor Aura When Equipped": [
        "151,56"
    ],
    "Level {} Thunder Storm Aura When Equipped": [
        "151,57"
    ],
    "Level {} Energy Shield Aura When Equipped": [
        "151,58"
    ],
    "Level {} Blizzard Aura When Equipped": [
        "151,59"
    ],
    "Level {} Chilling Armor Aura When Equipped": [
        "151,60"
    ],
    "Level {} Fire Mastery Aura When Equipped": [
        "151,61"
    ],
    "Level {} Hydra Aura When Equipped": [
        "151,62"
    ],
    "Level {} Lightning Mastery Aura When Equipped": [
        "151,63"
    ],
    "Level {} Frozen Orb Aura When Equipped": [
        "151,64"
    ],
    "Level {} Cold Mastery Aura When Equipped": [
        "151,65"
    ],
    "Level {} Amplify Damage Aura When Equipped": [
        "151,66"
    ],
    "Level {} Teeth Aura When Equipped": [
        "151,67"
    ],
    "Level {} Bone Armor Aura When Equipped": [
        "151,68"
    ],
    "Level {} Skeleton Mastery Aura When Equipped": [
        "151,69"
    ],
    "Level {} Raise Skeleton Aura When Equipped": [
        "151,70"
    ],
    "Level {} Dim Vision Aura When Equipped": [
        "151,71"
    ],
    "Level {} Weaken Aura When Equipped": [
        "151,72"
    ],
    "Level {} Poison Dagger Aura When Equipped": [
        "151,73"
    ],
    "Level {} Corpse Explosion Aura When Equipped": [
        "151,74"
    ],
    "Level {} Clay Golem Aura When Equipped": [
        "151,75"
    ],
    "Level {} Iron Maiden Aura When Equipped": [
        "151,76"
    ],
    "Level {} Terror Aura When Equipped": [
        "151,77"
    ],
    "Level {} Bone Wall Aura When Equipped": [
        "151,78"
    ],
    "Level {} Golem Mastery Aura When Equipped": [
        "151,79"
    ],
    "Level {} Raise Skeletal Mage Aura When Equipped": [
        "151,80"
    ],
    "Level {} Confuse Aura When Equipped": [
        "151,81"
    ],
    "Level {} Life Tap Aura When Equipped": [
        "151,82"
    ],
    "Level {} Poison Explosion Aura When Equipped": [
        "151,83"
    ],
    "Level {} Bone Spear Aura When Equipped": [
        "151,84"
    ],
    "Level {} Blood Golem Aura When Equipped": [
        "151,85"
    ],
    "Level {} Attract Aura When Equipped": [
        "151,86"
    ],
    "Level {} Decrepify Aura When Equipped": [
        "151,87"
    ],
    "Level {} Bone Prison Aura When Equipped": [
        "151,88"
    ],
    "Level {} Summon Resist Aura When Equipped": [
        "151,89"
    ],
    "Level {} Iron Golem Aura When Equipped": [
        "151,90"
    ],
    "Level {} Lower Resist Aura When Equipped": [
        "151,91"
    ],
    "Level {} Poison Nova Aura When Equipped": [
        "151,92"
    ],
    "Level {} Bone Spirit Aura When Equipped": [
        "151,93"
    ],
    "Level {} Fire Golem Aura When Equipped": [
        "151,94"
    ],
    "Level {} Revive Aura When Equipped": [
        "151,95"
    ],
    "Level {} Sacrifice Aura When Equipped": [
        "151,96"
    ],
    "Level {} Smite Aura When Equipped": [
        "151,97"
    ],
    "Level {} Might Aura When Equipped": [
        "151,98"
    ],
    "Level {} Prayer Aura When Equipped": [
        "151,99"
    ],
    "Level {} Resist Fire Aura When Equipped": [
        "151,100"
    ],
    "Level {} Holy Bolt Aura When Equipped": [
        "151,101"
    ],
    "Level {} Holy Fire Aura When Equipped": [
        "151,102"
    ],
    "Level {} Thorns Aura When Equipped": [
        "151,103"
    ],
    "Level {} Defiance Aura When Equipped": [
        "151,104"
    ],
    "Level {} Resist Cold Aura When Equipped": [
        "151,105"
    ],
    "Level {} Zeal Aura When Equipped": [
        "151,106"
    ],
    "Level {} Charge Aura When Equipped": [
        "151,107"
    ],
    "Level {} Blessed Aim Aura When Equipped": [
        "151,108"
    ],
    "Level {} Cleansing Aura When Equipped": [
        "151,109"
    ],
    "Level {} Resist Lightning Aura When Equipped": [
        "151,110"
    ],
    "Level {} Vengeance Aura When Equipped": [
        "151,111"
    ],
    "Level {} Blessed Hammer Aura When Equipped": [
        "151,112"
    ],
    "Level {} Concentration Aura When Equipped": [
        "151,113"
    ],
    "Level {} Holy Freeze Aura When Equipped": [
        "151,114"
    ],
    "Level {} Vigor Aura When Equipped": [
        "151,115"
    ],
    "Level {} Conversion Aura When Equipped": [
        "151,116"
    ],
    "Level {} Holy Shield Aura When Equipped": [
        "151,117"
    ],
    "Level {} Holy Shock Aura When Equipped": [
        "151,118"
    ],
    "Level {} Sanctuary Aura When Equipped": [
        "151,119"
    ],
    "Level {} Meditation Aura When Equipped": [
        "151,120"
    ],
    "Level {} Fist of the Heavens Aura When Equipped": [
        "151,121"
    ],
    "Level {} Fanaticism Aura When Equipped": [
        "151,122"
    ],
    "Level {} Conviction Aura When Equipped": [
        "151,123"
    ],
    "Level {} Redemption Aura When Equipped": [
        "151,124"
    ],
    "Level {} Salvation Aura When Equipped": [
        "151,125"
    ],
    "Level {} Bash Aura When Equipped": [
        "151,126"
    ],
    "Level {} Blade Mastery Aura When Equipped": [
        "151,127"
    ],
    "Level {} Axe Mastery Aura When Equipped": [
        "151,128"
    ],
    "Level {} Mace Mastery Aura When Equipped": [
        "151,129"
    ],
    "Level {} Howl Aura When Equipped": [
        "151,130"
    ],
    "Level {} Find Potion Aura When Equipped": [
        "151,131"
    ],
    "Level {} Leap Aura When Equipped": [
        "151,132"
    ],
    "Level {} Double Swing Aura When Equipped": [
        "151,133"
    ],
    "Level {} Polearm Mastery Aura When Equipped": [
        "151,134"
    ],
    "Level {} Throwing Mastery Aura When Equipped": [
        "151,135"
    ],
    "Level {} Spear Mastery Aura When Equipped": [
        "151,136"
    ],
    "Level {} Taunt Aura When Equipped": [
        "151,137"
    ],
    "Level {} Shout Aura When Equipped": [
        "151,138"
    ],
    "Level {} Stun Aura When Equipped": [
        "151,139"
    ],
    "Level {} Double Throw Aura When Equipped": [
        "151,140"
    ],
    "Level {} Increased Stamina Aura When Equipped": [
        "151,141"
    ],
    "Level {} Find Item Aura When Equipped": [
        "151,142"
    ],
    "Level {} Leap Attack Aura When Equipped": [
        "151,143"
    ],
    "Level {} Concentrate Aura When Equipped": [
        "151,144"
    ],
    "Level {} Iron Skin Aura When Equipped": [
        "151,145"
    ],
    "Level {} Battle Cry Aura When Equipped": [
        "151,146"
    ],
    "Level {} Frenzy Aura When Equipped": [
        "151,147"
    ],
    "Level {} Increased Speed Aura When Equipped": [
        "151,148"
    ],
    "Level {} Battle Orders Aura When Equipped": [
        "151,149"
    ],
    "Level {} Grim Ward Aura When Equipped": [
        "151,150"
    ],
    "Level {} Whirlwind Aura When Equipped": [
        "151,151"
    ],
    "Level {} Berserk Aura When Equipped": [
        "151,152"
    ],
    "Level {} Natural Resistance Aura When Equipped": [
        "151,153"
    ],
    "Level {} War Cry Aura When Equipped": [
        "151,154"
    ],
    "Level {} Battle Command Aura When Equipped": [
        "151,155"
    ],
    "Level {} Raven Aura When Equipped": [
        "151,221"
    ],
    "Level {} Poison Creeper Aura When Equipped": [
        "151,222"
    ],
    "Level {} Werewolf Aura When Equipped": [
        "151,223"
    ],
    "Level {} Lycanthropy Aura When Equipped": [
        "151,224"
    ],
    "Level {} Firestorm Aura When Equipped": [
        "151,225"
    ],
    "Level {} Oak Sage Aura When Equipped": [
        "151,226"
    ],
    "Level {} Summon Spirit Wolf Aura When Equipped": [
        "151,227"
    ],
    "Level {} Werebear Aura When Equipped": [
        "151,228"
    ],
    "Level {} Molten Boulder Aura When Equipped": [
        "151,229"
    ],
    "Level {} Arctic Blast Aura When Equipped": [
        "151,230"
    ],
    "Level {} Carrion Vine Aura When Equipped": [
        "151,231"
    ],
    "Level {} Feral Rage Aura When Equipped": [
        "151,232"
    ],
    "Level {} Maul Aura When Equipped": [
        "151,233"
    ],
    "Level {} Fissure Aura When Equipped": [
        "151,234"
    ],
    "Level {} Cyclone Armor Aura When Equipped": [
        "151,235"
    ],
    "Level {} Heart of Wolverine Aura When Equipped": [
        "151,236"
    ],
    "Level {} Summon Dire Wolf Aura When Equipped": [
        "151,237"
    ],
    "Level {} Rabies Aura When Equipped": [
        "151,238"
    ],
    "Level {} Fire Claws Aura When Equipped": [
        "151,239"
    ],
    "Level {} Twister Aura When Equipped": [
        "151,240"
    ],
    "Level {} Solar Creeper Aura When Equipped": [
        "151,241"
    ],
    "Level {} Hunger Aura When Equipped": [
        "151,242"
    ],
    "Level {} Shock Wave Aura When Equipped": [
        "151,243"
    ],
    "Level {} Volcano Aura When Equipped": [
        "151,244"
    ],
    "Level {} Tornado Aura When Equipped": [
        "151,245"
    ],
    "Level {} Spirit of Barbs Aura When Equipped": [
        "151,246"
    ],
    "Level {} Summon Grizzly Aura When Equipped": [
        "151,247"
    ],
    "Level {} Fury Aura When Equipped": [
        "151,248"
    ],
    "Level {} Armageddon Aura When Equipped": [
        "151,249"
    ],
    "Level {} Hurricane Aura When Equipped": [
        "151,250"
    ],
    "Level {} Fire Blast Aura When Equipped": [
        "151,251"
    ],
    "Level {} Claw Mastery Aura When Equipped": [
        "151,252"
    ],
    "Level {} Psychic Hammer Aura When Equipped": [
        "151,253"
    ],
    "Level {} Tiger Strike Aura When Equipped": [
        "151,254"
    ],
    "Level {} Dragon Talon Aura When Equipped": [
        "151,255"
    ],
    "Level {} Shock Web Aura When Equipped": [
        "151,256"
    ],
    "Level {} Blade Sentinel Aura When Equipped": [
        "151,257"
    ],
    "Level {} Burst of Speed Aura When Equipped": [
        "151,258"
    ],
    "Level {} Fists of Fire Aura When Equipped": [
        "151,259"
    ],
    "Level {} Dragon Claw Aura When Equipped": [
        "151,260"
    ],
    "Level {} Charged Bolt Sentry Aura When Equipped": [
        "151,261"
    ],
    "Level {} Wake of Fire Aura When Equipped": [
        "151,262"
    ],
    "Level {} Weapon Block Aura When Equipped": [
        "151,263"
    ],
    "Level {} Cloak of Shadows Aura When Equipped": [
        "151,264"
    ],
    "Level {} Cobra Strike Aura When Equipped": [
        "151,265"
    ],
    "Level {} Blade Fury Aura When Equipped": [
        "151,266"
    ],
    "Level {} Fade Aura When Equipped": [
        "151,267"
    ],
    "Level {} Shadow Warrior Aura When Equipped": [
        "151,268"
    ],
    "Level {} Claws of Thunder Aura When Equipped": [
        "151,269"
    ],
    "Level {} Dragon Tail Aura When Equipped": [
        "151,270"
    ],
    "Level {} Lightning Sentry Aura When Equipped": [
        "151,271"
    ],
    "Level {} Wake of Inferno Aura When Equipped": [
        "151,272"
    ],
    "Level {} Mind Blast Aura When Equipped": [
        "151,273"
    ],
    "Level {} Blades of Ice Aura When Equipped": [
        "151,274"
    ],
    "Level {} Dragon Flight Aura When Equipped": [
        "151,275"
    ],
    "Level {} Death Sentry Aura When Equipped": [
        "151,276"
    ],
    "Level {} Blade Shield Aura When Equipped": [
        "151,277"
    ],
    "Level {} Venom Aura When Equipped": [
        "151,278"
    ],
    "Level {} Shadow Master Aura When Equipped": [
        "151,279"
    ],
    "Level {} Phoenix Strike Aura When Equipped": [
        "151,280"
    ],
    "{}% Chance to cast level {} Magic Arrow on attack": [
        "195,6"
    ],
    "{}% Chance to cast level {} Fire Arrow on attack": [
        "195,7"
    ],
    "{}% Chance to cast level {} Inner Sight on attack": [
        "195,8"
    ],
    "{}% Chance to cast level {} Critical Strike on attack": [
        "195,9"
    ],
    "{}% Chance to cast level {} Jab on attack": [
        "195,10"
    ],
    "{}% Chance to cast level {} Cold Arrow on attack": [
        "195,11"
    ],
    "{}% Chance to cast level {} Multiple Shot on attack": [
        "195,12"
    ],
    "{}% Chance to cast level {} Dodge on attack": [
        "195,13"
    ],
    "{}% Chance to cast level {} Power Strike on attack": [
        "195,14"
    ],
    "{}% Chance to cast level {} Poison Javelin on attack": [
        "195,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow on attack": [
        "195,16"
    ],
    "{}% Chance to cast level {} Slow Missiles on attack": [
        "195,17"
    ],
    "{}% Chance to cast level {} Avoid on attack": [
        "195,18"
    ],
    "{}% Chance to cast level {} Impale on attack": [
        "195,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt on attack": [
        "195,20"
    ],
    "{}% Chance to cast level {} Ice Arrow on attack": [
        "195,21"
    ],
    "{}% Chance to cast level {} Guided Arrow on attack": [
        "195,22"
    ],
    "{}% Chance to cast level {} Penetrate on attack": [
        "195,23"
    ],
    "{}% Chance to cast level {} Charged Strike on attack": [
        "195,24"
    ],
    "{}% Chance to cast level {} Plague Javelin on attack": [
        "195,25"
    ],
    "{}% Chance to cast level {} Strafe on attack": [
        "195,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow on attack": [
        "195,27"
    ],
    "{}% Chance to cast level {} Decoy on attack": [
        "195,28"
    ],
    "{}% Chance to cast level {} Evade on attack": [
        "195,29"
    ],
    "{}% Chance to cast level {} Fend on attack": [
        "195,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow on attack": [
        "195,31"
    ],
    "{}% Chance to cast level {} Valkyrie on attack": [
        "195,32"
    ],
    "{}% Chance to cast level {} Pierce on attack": [
        "195,33"
    ],
    "{}% Chance to cast level {} Lightning Strike on attack": [
        "195,34"
    ],
    "{}% Chance to cast level {} Lightning Fury on attack": [
        "195,35"
    ],
    "{}% Chance to cast level {} Fire Bolt on attack": [
        "195,36"
    ],
    "{}% Chance to cast level {} Warmth on attack": [
        "195,37"
    ],
    "{}% Chance to cast level {} Charged Bolt on attack": [
        "195,38"
    ],
    "{}% Chance to cast level {} Ice Bolt on attack": [
        "195,39"
    ],
    "{}% Chance to cast level {} Frozen Armor on attack": [
        "195,40"
    ],
    "{}% Chance to cast level {} Inferno on attack": [
        "195,41"
    ],
    "{}% Chance to cast level {} Static Field on attack": [
        "195,42"
    ],
    "{}% Chance to cast level {} Telekinesis on attack": [
        "195,43"
    ],
    "{}% Chance to cast level {} Frost Nova on attack": [
        "195,44"
    ],
    "{}% Chance to cast level {} Ice Blast on attack": [
        "195,45"
    ],
    "{}% Chance to cast level {} Blaze on attack": [
        "195,46"
    ],
    "{}% Chance to cast level {} Fire Ball on attack": [
        "195,47"
    ],
    "{}% Chance to cast level {} Nova on attack": [
        "195,48"
    ],
    "{}% Chance to cast level {} Lightning on attack": [
        "195,49"
    ],
    "{}% Chance to cast level {} Shiver Armor on attack": [
        "195,50"
    ],
    "{}% Chance to cast level {} Fire Wall on attack": [
        "195,51"
    ],
    "{}% Chance to cast level {} Enchant on attack": [
        "195,52"
    ],
    "{}% Chance to cast level {} Chain Lightning on attack": [
        "195,53"
    ],
    "{}% Chance to cast level {} Teleport on attack": [
        "195,54"
    ],
    "{}% Chance to cast level {} Glacial Spike on attack": [
        "195,55"
    ],
    "{}% Chance to cast level {} Meteor on attack": [
        "195,56"
    ],
    "{}% Chance to cast level {} Thunder Storm on attack": [
        "195,57"
    ],
    "{}% Chance to cast level {} Energy Shield on attack": [
        "195,58"
    ],
    "{}% Chance to cast level {} Blizzard on attack": [
        "195,59"
    ],
    "{}% Chance to cast level {} Chilling Armor on attack": [
        "195,60"
    ],
    "{}% Chance to cast level {} Fire Mastery on attack": [
        "195,61"
    ],
    "{}% Chance to cast level {} Hydra on attack": [
        "195,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery on attack": [
        "195,63"
    ],
    "{}% Chance to cast level {} Frozen Orb on attack": [
        "195,64"
    ],
    "{}% Chance to cast level {} Cold Mastery on attack": [
        "195,65"
    ],
    "{}% Chance to cast level {} Amplify Damage on attack": [
        "195,66"
    ],
    "{}% Chance to cast level {} Teeth on attack": [
        "195,67"
    ],
    "{}% Chance to cast level {} Bone Armor on attack": [
        "195,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery on attack": [
        "195,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton on attack": [
        "195,70"
    ],
    "{}% Chance to cast level {} Dim Vision on attack": [
        "195,71"
    ],
    "{}% Chance to cast level {} Weaken on attack": [
        "195,72"
    ],
    "{}% Chance to cast level {} Poison Dagger on attack": [
        "195,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion on attack": [
        "195,74"
    ],
    "{}% Chance to cast level {} Clay Golem on attack": [
        "195,75"
    ],
    "{}% Chance to cast level {} Iron Maiden on attack": [
        "195,76"
    ],
    "{}% Chance to cast level {} Terror on attack": [
        "195,77"
    ],
    "{}% Chance to cast level {} Bone Wall on attack": [
        "195,78"
    ],
    "{}% Chance to cast level {} Golem Mastery on attack": [
        "195,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage on attack": [
        "195,80"
    ],
    "{}% Chance to cast level {} Confuse on attack": [
        "195,81"
    ],
    "{}% Chance to cast level {} Life Tap on attack": [
        "195,82"
    ],
    "{}% Chance to cast level {} Poison Explosion on attack": [
        "195,83"
    ],
    "{}% Chance to cast level {} Bone Spear on attack": [
        "195,84"
    ],
    "{}% Chance to cast level {} Blood Golem on attack": [
        "195,85"
    ],
    "{}% Chance to cast level {} Attract on attack": [
        "195,86"
    ],
    "{}% Chance to cast level {} Decrepify on attack": [
        "195,87"
    ],
    "{}% Chance to cast level {} Bone Prison on attack": [
        "195,88"
    ],
    "{}% Chance to cast level {} Summon Resist on attack": [
        "195,89"
    ],
    "{}% Chance to cast level {} Iron Golem on attack": [
        "195,90"
    ],
    "{}% Chance to cast level {} Lower Resist on attack": [
        "195,91"
    ],
    "{}% Chance to cast level {} Poison Nova on attack": [
        "195,92"
    ],
    "{}% Chance to cast level {} Bone Spirit on attack": [
        "195,93"
    ],
    "{}% Chance to cast level {} Fire Golem on attack": [
        "195,94"
    ],
    "{}% Chance to cast level {} Revive on attack": [
        "195,95"
    ],
    "{}% Chance to cast level {} Sacrifice on attack": [
        "195,96"
    ],
    "{}% Chance to cast level {} Smite on attack": [
        "195,97"
    ],
    "{}% Chance to cast level {} Might on attack": [
        "195,98"
    ],
    "{}% Chance to cast level {} Prayer on attack": [
        "195,99"
    ],
    "{}% Chance to cast level {} Resist Fire on attack": [
        "195,100"
    ],
    "{}% Chance to cast level {} Holy Bolt on attack": [
        "195,101"
    ],
    "{}% Chance to cast level {} Holy Fire on attack": [
        "195,102"
    ],
    "{}% Chance to cast level {} Thorns on attack": [
        "195,103"
    ],
    "{}% Chance to cast level {} Defiance on attack": [
        "195,104"
    ],
    "{}% Chance to cast level {} Resist Cold on attack": [
        "195,105"
    ],
    "{}% Chance to cast level {} Zeal on attack": [
        "195,106"
    ],
    "{}% Chance to cast level {} Charge on attack": [
        "195,107"
    ],
    "{}% Chance to cast level {} Blessed Aim on attack": [
        "195,108"
    ],
    "{}% Chance to cast level {} Cleansing on attack": [
        "195,109"
    ],
    "{}% Chance to cast level {} Resist Lightning on attack": [
        "195,110"
    ],
    "{}% Chance to cast level {} Vengeance on attack": [
        "195,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer on attack": [
        "195,112"
    ],
    "{}% Chance to cast level {} Concentration on attack": [
        "195,113"
    ],
    "{}% Chance to cast level {} Holy Freeze on attack": [
        "195,114"
    ],
    "{}% Chance to cast level {} Vigor on attack": [
        "195,115"
    ],
    "{}% Chance to cast level {} Conversion on attack": [
        "195,116"
    ],
    "{}% Chance to cast level {} Holy Shield on attack": [
        "195,117"
    ],
    "{}% Chance to cast level {} Holy Shock on attack": [
        "195,118"
    ],
    "{}% Chance to cast level {} Sanctuary on attack": [
        "195,119"
    ],
    "{}% Chance to cast level {} Meditation on attack": [
        "195,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens on attack": [
        "195,121"
    ],
    "{}% Chance to cast level {} Fanaticism on attack": [
        "195,122"
    ],
    "{}% Chance to cast level {} Conviction on attack": [
        "195,123"
    ],
    "{}% Chance to cast level {} Redemption on attack": [
        "195,124"
    ],
    "{}% Chance to cast level {} Salvation on attack": [
        "195,125"
    ],
    "{}% Chance to cast level {} Bash on attack": [
        "195,126"
    ],
    "{}% Chance to cast level {} Blade Mastery on attack": [
        "195,127"
    ],
    "{}% Chance to cast level {} Axe Mastery on attack": [
        "195,128"
    ],
    "{}% Chance to cast level {} Mace Mastery on attack": [
        "195,129"
    ],
    "{}% Chance to cast level {} Howl on attack": [
        "195,130"
    ],
    "{}% Chance to cast level {} Find Potion on attack": [
        "195,131"
    ],
    "{}% Chance to cast level {} Leap on attack": [
        "195,132"
    ],
    "{}% Chance to cast level {} Double Swing on attack": [
        "195,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery on attack": [
        "195,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery on attack": [
        "195,135"
    ],
    "{}% Chance to cast level {} Spear Mastery on attack": [
        "195,136"
    ],
    "{}% Chance to cast level {} Taunt on attack": [
        "195,137"
    ],
    "{}% Chance to cast level {} Shout on attack": [
        "195,138"
    ],
    "{}% Chance to cast level {} Stun on attack": [
        "195,139"
    ],
    "{}% Chance to cast level {} Double Throw on attack": [
        "195,140"
    ],
    "{}% Chance to cast level {} Increased Stamina on attack": [
        "195,141"
    ],
    "{}% Chance to cast level {} Find Item on attack": [
        "195,142"
    ],
    "{}% Chance to cast level {} Leap Attack on attack": [
        "195,143"
    ],
    "{}% Chance to cast level {} Concentrate on attack": [
        "195,144"
    ],
    "{}% Chance to cast level {} Iron Skin on attack": [
        "195,145"
    ],
    "{}% Chance to cast level {} Battle Cry on attack": [
        "195,146"
    ],
    "{}% Chance to cast level {} Frenzy on attack": [
        "195,147"
    ],
    "{}% Chance to cast level {} Increased Speed on attack": [
        "195,148"
    ],
    "{}% Chance to cast level {} Battle Orders on attack": [
        "195,149"
    ],
    "{}% Chance to cast level {} Grim Ward on attack": [
        "195,150"
    ],
    "{}% Chance to cast level {} Whirlwind on attack": [
        "195,151"
    ],
    "{}% Chance to cast level {} Berserk on attack": [
        "195,152"
    ],
    "{}% Chance to cast level {} Natural Resistance on attack": [
        "195,153"
    ],
    "{}% Chance to cast level {} War Cry on attack": [
        "195,154"
    ],
    "{}% Chance to cast level {} Battle Command on attack": [
        "195,155"
    ],
    "{}% Chance to cast level {} Raven on attack": [
        "195,221"
    ],
    "{}% Chance to cast level {} Poison Creeper on attack": [
        "195,222"
    ],
    "{}% Chance to cast level {} Werewolf on attack": [
        "195,223"
    ],
    "{}% Chance to cast level {} Lycanthropy on attack": [
        "195,224"
    ],
    "{}% Chance to cast level {} Firestorm on attack": [
        "195,225"
    ],
    "{}% Chance to cast level {} Oak Sage on attack": [
        "195,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf on attack": [
        "195,227"
    ],
    "{}% Chance to cast level {} Werebear on attack": [
        "195,228"
    ],
    "{}% Chance to cast level {} Molten Boulder on attack": [
        "195,229"
    ],
    "{}% Chance to cast level {} Arctic Blast on attack": [
        "195,230"
    ],
    "{}% Chance to cast level {} Carrion Vine on attack": [
        "195,231"
    ],
    "{}% Chance to cast level {} Feral Rage on attack": [
        "195,232"
    ],
    "{}% Chance to cast level {} Maul on attack": [
        "195,233"
    ],
    "{}% Chance to cast level {} Fissure on attack": [
        "195,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor on attack": [
        "195,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine on attack": [
        "195,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf on attack": [
        "195,237"
    ],
    "{}% Chance to cast level {} Rabies on attack": [
        "195,238"
    ],
    "{}% Chance to cast level {} Fire Claws on attack": [
        "195,239"
    ],
    "{}% Chance to cast level {} Twister on attack": [
        "195,240"
    ],
    "{}% Chance to cast level {} Solar Creeper on attack": [
        "195,241"
    ],
    "{}% Chance to cast level {} Hunger on attack": [
        "195,242"
    ],
    "{}% Chance to cast level {} Shock Wave on attack": [
        "195,243"
    ],
    "{}% Chance to cast level {} Volcano on attack": [
        "195,244"
    ],
    "{}% Chance to cast level {} Tornado on attack": [
        "195,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs on attack": [
        "195,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly on attack": [
        "195,247"
    ],
    "{}% Chance to cast level {} Fury on attack": [
        "195,248"
    ],
    "{}% Chance to cast level {} Armageddon on attack": [
        "195,249"
    ],
    "{}% Chance to cast level {} Hurricane on attack": [
        "195,250"
    ],
    "{}% Chance to cast level {} Fire Blast on attack": [
        "195,251"
    ],
    "{}% Chance to cast level {} Claw Mastery on attack": [
        "195,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer on attack": [
        "195,253"
    ],
    "{}% Chance to cast level {} Tiger Strike on attack": [
        "195,254"
    ],
    "{}% Chance to cast level {} Dragon Talon on attack": [
        "195,255"
    ],
    "{}% Chance to cast level {} Shock Web on attack": [
        "195,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel on attack": [
        "195,257"
    ],
    "{}% Chance to cast level {} Burst of Speed on attack": [
        "195,258"
    ],
    "{}% Chance to cast level {} Fists of Fire on attack": [
        "195,259"
    ],
    "{}% Chance to cast level {} Dragon Claw on attack": [
        "195,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry on attack": [
        "195,261"
    ],
    "{}% Chance to cast level {} Wake of Fire on attack": [
        "195,262"
    ],
    "{}% Chance to cast level {} Weapon Block on attack": [
        "195,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows on attack": [
        "195,264"
    ],
    "{}% Chance to cast level {} Cobra Strike on attack": [
        "195,265"
    ],
    "{}% Chance to cast level {} Blade Fury on attack": [
        "195,266"
    ],
    "{}% Chance to cast level {} Fade on attack": [
        "195,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior on attack": [
        "195,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder on attack": [
        "195,269"
    ],
    "{}% Chance to cast level {} Dragon Tail on attack": [
        "195,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry on attack": [
        "195,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno on attack": [
        "195,272"
    ],
    "{}% Chance to cast level {} Mind Blast on attack": [
        "195,273"
    ],
    "{}% Chance to cast level {} Blades of Ice on attack": [
        "195,274"
    ],
    "{}% Chance to cast level {} Dragon Flight on attack": [
        "195,275"
    ],
    "{}% Chance to cast level {} Death Sentry on attack": [
        "195,276"
    ],
    "{}% Chance to cast level {} Blade Shield on attack": [
        "195,277"
    ],
    "{}% Chance to cast level {} Venom on attack": [
        "195,278"
    ],
    "{}% Chance to cast level {} Shadow Master on attack": [
        "195,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike on attack": [
        "195,280"
    ],
    "{}% Chance to cast level {} Magic Arrow on striking": [
        "198,6"
    ],
    "{}% Chance to cast level {} Fire Arrow on striking": [
        "198,7"
    ],
    "{}% Chance to cast level {} Inner Sight on striking": [
        "198,8"
    ],
    "{}% Chance to cast level {} Critical Strike on striking": [
        "198,9"
    ],
    "{}% Chance to cast level {} Jab on striking": [
        "198,10"
    ],
    "{}% Chance to cast level {} Cold Arrow on striking": [
        "198,11"
    ],
    "{}% Chance to cast level {} Multiple Shot on striking": [
        "198,12"
    ],
    "{}% Chance to cast level {} Dodge on striking": [
        "198,13"
    ],
    "{}% Chance to cast level {} Power Strike on striking": [
        "198,14"
    ],
    "{}% Chance to cast level {} Poison Javelin on striking": [
        "198,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow on striking": [
        "198,16"
    ],
    "{}% Chance to cast level {} Slow Missiles on striking": [
        "198,17"
    ],
    "{}% Chance to cast level {} Avoid on striking": [
        "198,18"
    ],
    "{}% Chance to cast level {} Impale on striking": [
        "198,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt on striking": [
        "198,20"
    ],
    "{}% Chance to cast level {} Ice Arrow on striking": [
        "198,21"
    ],
    "{}% Chance to cast level {} Guided Arrow on striking": [
        "198,22"
    ],
    "{}% Chance to cast level {} Penetrate on striking": [
        "198,23"
    ],
    "{}% Chance to cast level {} Charged Strike on striking": [
        "198,24"
    ],
    "{}% Chance to cast level {} Plague Javelin on striking": [
        "198,25"
    ],
    "{}% Chance to cast level {} Strafe on striking": [
        "198,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow on striking": [
        "198,27"
    ],
    "{}% Chance to cast level {} Decoy on striking": [
        "198,28"
    ],
    "{}% Chance to cast level {} Evade on striking": [
        "198,29"
    ],
    "{}% Chance to cast level {} Fend on striking": [
        "198,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow on striking": [
        "198,31"
    ],
    "{}% Chance to cast level {} Valkyrie on striking": [
        "198,32"
    ],
    "{}% Chance to cast level {} Pierce on striking": [
        "198,33"
    ],
    "{}% Chance to cast level {} Lightning Strike on striking": [
        "198,34"
    ],
    "{}% Chance to cast level {} Lightning Fury on striking": [
        "198,35"
    ],
    "{}% Chance to cast level {} Fire Bolt on striking": [
        "198,36"
    ],
    "{}% Chance to cast level {} Warmth on striking": [
        "198,37"
    ],
    "{}% Chance to cast level {} Charged Bolt on striking": [
        "198,38"
    ],
    "{}% Chance to cast level {} Ice Bolt on striking": [
        "198,39"
    ],
    "{}% Chance to cast level {} Frozen Armor on striking": [
        "198,40"
    ],
    "{}% Chance to cast level {} Inferno on striking": [
        "198,41"
    ],
    "{}% Chance to cast level {} Static Field on striking": [
        "198,42"
    ],
    "{}% Chance to cast level {} Telekinesis on striking": [
        "198,43"
    ],
    "{}% Chance to cast level {} Frost Nova on striking": [
        "198,44"
    ],
    "{}% Chance to cast level {} Ice Blast on striking": [
        "198,45"
    ],
    "{}% Chance to cast level {} Blaze on striking": [
        "198,46"
    ],
    "{}% Chance to cast level {} Fire Ball on striking": [
        "198,47"
    ],
    "{}% Chance to cast level {} Nova on striking": [
        "198,48"
    ],
    "{}% Chance to cast level {} Lightning on striking": [
        "198,49"
    ],
    "{}% Chance to cast level {} Shiver Armor on striking": [
        "198,50"
    ],
    "{}% Chance to cast level {} Fire Wall on striking": [
        "198,51"
    ],
    "{}% Chance to cast level {} Enchant on striking": [
        "198,52"
    ],
    "{}% Chance to cast level {} Chain Lightning on striking": [
        "198,53"
    ],
    "{}% Chance to cast level {} Teleport on striking": [
        "198,54"
    ],
    "{}% Chance to cast level {} Glacial Spike on striking": [
        "198,55"
    ],
    "{}% Chance to cast level {} Meteor on striking": [
        "198,56"
    ],
    "{}% Chance to cast level {} Thunder Storm on striking": [
        "198,57"
    ],
    "{}% Chance to cast level {} Energy Shield on striking": [
        "198,58"
    ],
    "{}% Chance to cast level {} Blizzard on striking": [
        "198,59"
    ],
    "{}% Chance to cast level {} Chilling Armor on striking": [
        "198,60"
    ],
    "{}% Chance to cast level {} Fire Mastery on striking": [
        "198,61"
    ],
    "{}% Chance to cast level {} Hydra on striking": [
        "198,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery on striking": [
        "198,63"
    ],
    "{}% Chance to cast level {} Frozen Orb on striking": [
        "198,64"
    ],
    "{}% Chance to cast level {} Cold Mastery on striking": [
        "198,65"
    ],
    "{}% Chance to cast level {} Amplify Damage on striking": [
        "198,66"
    ],
    "{}% Chance to cast level {} Teeth on striking": [
        "198,67"
    ],
    "{}% Chance to cast level {} Bone Armor on striking": [
        "198,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery on striking": [
        "198,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton on striking": [
        "198,70"
    ],
    "{}% Chance to cast level {} Dim Vision on striking": [
        "198,71"
    ],
    "{}% Chance to cast level {} Weaken on striking": [
        "198,72"
    ],
    "{}% Chance to cast level {} Poison Dagger on striking": [
        "198,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion on striking": [
        "198,74"
    ],
    "{}% Chance to cast level {} Clay Golem on striking": [
        "198,75"
    ],
    "{}% Chance to cast level {} Iron Maiden on striking": [
        "198,76"
    ],
    "{}% Chance to cast level {} Terror on striking": [
        "198,77"
    ],
    "{}% Chance to cast level {} Bone Wall on striking": [
        "198,78"
    ],
    "{}% Chance to cast level {} Golem Mastery on striking": [
        "198,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage on striking": [
        "198,80"
    ],
    "{}% Chance to cast level {} Confuse on striking": [
        "198,81"
    ],
    "{}% Chance to cast level {} Life Tap on striking": [
        "198,82"
    ],
    "{}% Chance to cast level {} Poison Explosion on striking": [
        "198,83"
    ],
    "{}% Chance to cast level {} Bone Spear on striking": [
        "198,84"
    ],
    "{}% Chance to cast level {} Blood Golem on striking": [
        "198,85"
    ],
    "{}% Chance to cast level {} Attract on striking": [
        "198,86"
    ],
    "{}% Chance to cast level {} Decrepify on striking": [
        "198,87"
    ],
    "{}% Chance to cast level {} Bone Prison on striking": [
        "198,88"
    ],
    "{}% Chance to cast level {} Summon Resist on striking": [
        "198,89"
    ],
    "{}% Chance to cast level {} Iron Golem on striking": [
        "198,90"
    ],
    "{}% Chance to cast level {} Lower Resist on striking": [
        "198,91"
    ],
    "{}% Chance to cast level {} Poison Nova on striking": [
        "198,92"
    ],
    "{}% Chance to cast level {} Bone Spirit on striking": [
        "198,93"
    ],
    "{}% Chance to cast level {} Fire Golem on striking": [
        "198,94"
    ],
    "{}% Chance to cast level {} Revive on striking": [
        "198,95"
    ],
    "{}% Chance to cast level {} Sacrifice on striking": [
        "198,96"
    ],
    "{}% Chance to cast level {} Smite on striking": [
        "198,97"
    ],
    "{}% Chance to cast level {} Might on striking": [
        "198,98"
    ],
    "{}% Chance to cast level {} Prayer on striking": [
        "198,99"
    ],
    "{}% Chance to cast level {} Resist Fire on striking": [
        "198,100"
    ],
    "{}% Chance to cast level {} Holy Bolt on striking": [
        "198,101"
    ],
    "{}% Chance to cast level {} Holy Fire on striking": [
        "198,102"
    ],
    "{}% Chance to cast level {} Thorns on striking": [
        "198,103"
    ],
    "{}% Chance to cast level {} Defiance on striking": [
        "198,104"
    ],
    "{}% Chance to cast level {} Resist Cold on striking": [
        "198,105"
    ],
    "{}% Chance to cast level {} Zeal on striking": [
        "198,106"
    ],
    "{}% Chance to cast level {} Charge on striking": [
        "198,107"
    ],
    "{}% Chance to cast level {} Blessed Aim on striking": [
        "198,108"
    ],
    "{}% Chance to cast level {} Cleansing on striking": [
        "198,109"
    ],
    "{}% Chance to cast level {} Resist Lightning on striking": [
        "198,110"
    ],
    "{}% Chance to cast level {} Vengeance on striking": [
        "198,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer on striking": [
        "198,112"
    ],
    "{}% Chance to cast level {} Concentration on striking": [
        "198,113"
    ],
    "{}% Chance to cast level {} Holy Freeze on striking": [
        "198,114"
    ],
    "{}% Chance to cast level {} Vigor on striking": [
        "198,115"
    ],
    "{}% Chance to cast level {} Conversion on striking": [
        "198,116"
    ],
    "{}% Chance to cast level {} Holy Shield on striking": [
        "198,117"
    ],
    "{}% Chance to cast level {} Holy Shock on striking": [
        "198,118"
    ],
    "{}% Chance to cast level {} Sanctuary on striking": [
        "198,119"
    ],
    "{}% Chance to cast level {} Meditation on striking": [
        "198,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens on striking": [
        "198,121"
    ],
    "{}% Chance to cast level {} Fanaticism on striking": [
        "198,122"
    ],
    "{}% Chance to cast level {} Conviction on striking": [
        "198,123"
    ],
    "{}% Chance to cast level {} Redemption on striking": [
        "198,124"
    ],
    "{}% Chance to cast level {} Salvation on striking": [
        "198,125"
    ],
    "{}% Chance to cast level {} Bash on striking": [
        "198,126"
    ],
    "{}% Chance to cast level {} Blade Mastery on striking": [
        "198,127"
    ],
    "{}% Chance to cast level {} Axe Mastery on striking": [
        "198,128"
    ],
    "{}% Chance to cast level {} Mace Mastery on striking": [
        "198,129"
    ],
    "{}% Chance to cast level {} Howl on striking": [
        "198,130"
    ],
    "{}% Chance to cast level {} Find Potion on striking": [
        "198,131"
    ],
    "{}% Chance to cast level {} Leap on striking": [
        "198,132"
    ],
    "{}% Chance to cast level {} Double Swing on striking": [
        "198,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery on striking": [
        "198,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery on striking": [
        "198,135"
    ],
    "{}% Chance to cast level {} Spear Mastery on striking": [
        "198,136"
    ],
    "{}% Chance to cast level {} Taunt on striking": [
        "198,137"
    ],
    "{}% Chance to cast level {} Shout on striking": [
        "198,138"
    ],
    "{}% Chance to cast level {} Stun on striking": [
        "198,139"
    ],
    "{}% Chance to cast level {} Double Throw on striking": [
        "198,140"
    ],
    "{}% Chance to cast level {} Increased Stamina on striking": [
        "198,141"
    ],
    "{}% Chance to cast level {} Find Item on striking": [
        "198,142"
    ],
    "{}% Chance to cast level {} Leap Attack on striking": [
        "198,143"
    ],
    "{}% Chance to cast level {} Concentrate on striking": [
        "198,144"
    ],
    "{}% Chance to cast level {} Iron Skin on striking": [
        "198,145"
    ],
    "{}% Chance to cast level {} Battle Cry on striking": [
        "198,146"
    ],
    "{}% Chance to cast level {} Frenzy on striking": [
        "198,147"
    ],
    "{}% Chance to cast level {} Increased Speed on striking": [
        "198,148"
    ],
    "{}% Chance to cast level {} Battle Orders on striking": [
        "198,149"
    ],
    "{}% Chance to cast level {} Grim Ward on striking": [
        "198,150"
    ],
    "{}% Chance to cast level {} Whirlwind on striking": [
        "198,151"
    ],
    "{}% Chance to cast level {} Berserk on striking": [
        "198,152"
    ],
    "{}% Chance to cast level {} Natural Resistance on striking": [
        "198,153"
    ],
    "{}% Chance to cast level {} War Cry on striking": [
        "198,154"
    ],
    "{}% Chance to cast level {} Battle Command on striking": [
        "198,155"
    ],
    "{}% Chance to cast level {} Raven on striking": [
        "198,221"
    ],
    "{}% Chance to cast level {} Poison Creeper on striking": [
        "198,222"
    ],
    "{}% Chance to cast level {} Werewolf on striking": [
        "198,223"
    ],
    "{}% Chance to cast level {} Lycanthropy on striking": [
        "198,224"
    ],
    "{}% Chance to cast level {} Firestorm on striking": [
        "198,225"
    ],
    "{}% Chance to cast level {} Oak Sage on striking": [
        "198,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf on striking": [
        "198,227"
    ],
    "{}% Chance to cast level {} Werebear on striking": [
        "198,228"
    ],
    "{}% Chance to cast level {} Molten Boulder on striking": [
        "198,229"
    ],
    "{}% Chance to cast level {} Arctic Blast on striking": [
        "198,230"
    ],
    "{}% Chance to cast level {} Carrion Vine on striking": [
        "198,231"
    ],
    "{}% Chance to cast level {} Feral Rage on striking": [
        "198,232"
    ],
    "{}% Chance to cast level {} Maul on striking": [
        "198,233"
    ],
    "{}% Chance to cast level {} Fissure on striking": [
        "198,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor on striking": [
        "198,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine on striking": [
        "198,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf on striking": [
        "198,237"
    ],
    "{}% Chance to cast level {} Rabies on striking": [
        "198,238"
    ],
    "{}% Chance to cast level {} Fire Claws on striking": [
        "198,239"
    ],
    "{}% Chance to cast level {} Twister on striking": [
        "198,240"
    ],
    "{}% Chance to cast level {} Solar Creeper on striking": [
        "198,241"
    ],
    "{}% Chance to cast level {} Hunger on striking": [
        "198,242"
    ],
    "{}% Chance to cast level {} Shock Wave on striking": [
        "198,243"
    ],
    "{}% Chance to cast level {} Volcano on striking": [
        "198,244"
    ],
    "{}% Chance to cast level {} Tornado on striking": [
        "198,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs on striking": [
        "198,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly on striking": [
        "198,247"
    ],
    "{}% Chance to cast level {} Fury on striking": [
        "198,248"
    ],
    "{}% Chance to cast level {} Armageddon on striking": [
        "198,249"
    ],
    "{}% Chance to cast level {} Hurricane on striking": [
        "198,250"
    ],
    "{}% Chance to cast level {} Fire Blast on striking": [
        "198,251"
    ],
    "{}% Chance to cast level {} Claw Mastery on striking": [
        "198,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer on striking": [
        "198,253"
    ],
    "{}% Chance to cast level {} Tiger Strike on striking": [
        "198,254"
    ],
    "{}% Chance to cast level {} Dragon Talon on striking": [
        "198,255"
    ],
    "{}% Chance to cast level {} Shock Web on striking": [
        "198,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel on striking": [
        "198,257"
    ],
    "{}% Chance to cast level {} Burst of Speed on striking": [
        "198,258"
    ],
    "{}% Chance to cast level {} Fists of Fire on striking": [
        "198,259"
    ],
    "{}% Chance to cast level {} Dragon Claw on striking": [
        "198,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry on striking": [
        "198,261"
    ],
    "{}% Chance to cast level {} Wake of Fire on striking": [
        "198,262"
    ],
    "{}% Chance to cast level {} Weapon Block on striking": [
        "198,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows on striking": [
        "198,264"
    ],
    "{}% Chance to cast level {} Cobra Strike on striking": [
        "198,265"
    ],
    "{}% Chance to cast level {} Blade Fury on striking": [
        "198,266"
    ],
    "{}% Chance to cast level {} Fade on striking": [
        "198,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior on striking": [
        "198,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder on striking": [
        "198,269"
    ],
    "{}% Chance to cast level {} Dragon Tail on striking": [
        "198,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry on striking": [
        "198,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno on striking": [
        "198,272"
    ],
    "{}% Chance to cast level {} Mind Blast on striking": [
        "198,273"
    ],
    "{}% Chance to cast level {} Blades of Ice on striking": [
        "198,274"
    ],
    "{}% Chance to cast level {} Dragon Flight on striking": [
        "198,275"
    ],
    "{}% Chance to cast level {} Death Sentry on striking": [
        "198,276"
    ],
    "{}% Chance to cast level {} Blade Shield on striking": [
        "198,277"
    ],
    "{}% Chance to cast level {} Venom on striking": [
        "198,278"
    ],
    "{}% Chance to cast level {} Shadow Master on striking": [
        "198,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike on striking": [
        "198,280"
    ],
    "{}% Chance to cast level {} Magic Arrow when struck": [
        "201,6"
    ],
    "{}% Chance to cast level {} Fire Arrow when struck": [
        "201,7"
    ],
    "{}% Chance to cast level {} Inner Sight when struck": [
        "201,8"
    ],
    "{}% Chance to cast level {} Critical Strike when struck": [
        "201,9"
    ],
    "{}% Chance to cast level {} Jab when struck": [
        "201,10"
    ],
    "{}% Chance to cast level {} Cold Arrow when struck": [
        "201,11"
    ],
    "{}% Chance to cast level {} Multiple Shot when struck": [
        "201,12"
    ],
    "{}% Chance to cast level {} Dodge when struck": [
        "201,13"
    ],
    "{}% Chance to cast level {} Power Strike when struck": [
        "201,14"
    ],
    "{}% Chance to cast level {} Poison Javelin when struck": [
        "201,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow when struck": [
        "201,16"
    ],
    "{}% Chance to cast level {} Slow Missiles when struck": [
        "201,17"
    ],
    "{}% Chance to cast level {} Avoid when struck": [
        "201,18"
    ],
    "{}% Chance to cast level {} Impale when struck": [
        "201,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt when struck": [
        "201,20"
    ],
    "{}% Chance to cast level {} Ice Arrow when struck": [
        "201,21"
    ],
    "{}% Chance to cast level {} Guided Arrow when struck": [
        "201,22"
    ],
    "{}% Chance to cast level {} Penetrate when struck": [
        "201,23"
    ],
    "{}% Chance to cast level {} Charged Strike when struck": [
        "201,24"
    ],
    "{}% Chance to cast level {} Plague Javelin when struck": [
        "201,25"
    ],
    "{}% Chance to cast level {} Strafe when struck": [
        "201,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow when struck": [
        "201,27"
    ],
    "{}% Chance to cast level {} Decoy when struck": [
        "201,28"
    ],
    "{}% Chance to cast level {} Evade when struck": [
        "201,29"
    ],
    "{}% Chance to cast level {} Fend when struck": [
        "201,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow when struck": [
        "201,31"
    ],
    "{}% Chance to cast level {} Valkyrie when struck": [
        "201,32"
    ],
    "{}% Chance to cast level {} Pierce when struck": [
        "201,33"
    ],
    "{}% Chance to cast level {} Lightning Strike when struck": [
        "201,34"
    ],
    "{}% Chance to cast level {} Lightning Fury when struck": [
        "201,35"
    ],
    "{}% Chance to cast level {} Fire Bolt when struck": [
        "201,36"
    ],
    "{}% Chance to cast level {} Warmth when struck": [
        "201,37"
    ],
    "{}% Chance to cast level {} Charged Bolt when struck": [
        "201,38"
    ],
    "{}% Chance to cast level {} Ice Bolt when struck": [
        "201,39"
    ],
    "{}% Chance to cast level {} Frozen Armor when struck": [
        "201,40"
    ],
    "{}% Chance to cast level {} Inferno when struck": [
        "201,41"
    ],
    "{}% Chance to cast level {} Static Field when struck": [
        "201,42"
    ],
    "{}% Chance to cast level {} Telekinesis when struck": [
        "201,43"
    ],
    "{}% Chance to cast level {} Frost Nova when struck": [
        "201,44"
    ],
    "{}% Chance to cast level {} Ice Blast when struck": [
        "201,45"
    ],
    "{}% Chance to cast level {} Blaze when struck": [
        "201,46"
    ],
    "{}% Chance to cast level {} Fire Ball when struck": [
        "201,47"
    ],
    "{}% Chance to cast level {} Nova when struck": [
        "201,48"
    ],
    "{}% Chance to cast level {} Lightning when struck": [
        "201,49"
    ],
    "{}% Chance to cast level {} Shiver Armor when struck": [
        "201,50"
    ],
    "{}% Chance to cast level {} Fire Wall when struck": [
        "201,51"
    ],
    "{}% Chance to cast level {} Enchant when struck": [
        "201,52"
    ],
    "{}% Chance to cast level {} Chain Lightning when struck": [
        "201,53"
    ],
    "{}% Chance to cast level {} Teleport when struck": [
        "201,54"
    ],
    "{}% Chance to cast level {} Glacial Spike when struck": [
        "201,55"
    ],
    "{}% Chance to cast level {} Meteor when struck": [
        "201,56"
    ],
    "{}% Chance to cast level {} Thunder Storm when struck": [
        "201,57"
    ],
    "{}% Chance to cast level {} Energy Shield when struck": [
        "201,58"
    ],
    "{}% Chance to cast level {} Blizzard when struck": [
        "201,59"
    ],
    "{}% Chance to cast level {} Chilling Armor when struck": [
        "201,60"
    ],
    "{}% Chance to cast level {} Fire Mastery when struck": [
        "201,61"
    ],
    "{}% Chance to cast level {} Hydra when struck": [
        "201,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery when struck": [
        "201,63"
    ],
    "{}% Chance to cast level {} Frozen Orb when struck": [
        "201,64"
    ],
    "{}% Chance to cast level {} Cold Mastery when struck": [
        "201,65"
    ],
    "{}% Chance to cast level {} Amplify Damage when struck": [
        "201,66"
    ],
    "{}% Chance to cast level {} Teeth when struck": [
        "201,67"
    ],
    "{}% Chance to cast level {} Bone Armor when struck": [
        "201,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery when struck": [
        "201,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton when struck": [
        "201,70"
    ],
    "{}% Chance to cast level {} Dim Vision when struck": [
        "201,71"
    ],
    "{}% Chance to cast level {} Weaken when struck": [
        "201,72"
    ],
    "{}% Chance to cast level {} Poison Dagger when struck": [
        "201,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion when struck": [
        "201,74"
    ],
    "{}% Chance to cast level {} Clay Golem when struck": [
        "201,75"
    ],
    "{}% Chance to cast level {} Iron Maiden when struck": [
        "201,76"
    ],
    "{}% Chance to cast level {} Terror when struck": [
        "201,77"
    ],
    "{}% Chance to cast level {} Bone Wall when struck": [
        "201,78"
    ],
    "{}% Chance to cast level {} Golem Mastery when struck": [
        "201,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage when struck": [
        "201,80"
    ],
    "{}% Chance to cast level {} Confuse when struck": [
        "201,81"
    ],
    "{}% Chance to cast level {} Life Tap when struck": [
        "201,82"
    ],
    "{}% Chance to cast level {} Poison Explosion when struck": [
        "201,83"
    ],
    "{}% Chance to cast level {} Bone Spear when struck": [
        "201,84"
    ],
    "{}% Chance to cast level {} Blood Golem when struck": [
        "201,85"
    ],
    "{}% Chance to cast level {} Attract when struck": [
        "201,86"
    ],
    "{}% Chance to cast level {} Decrepify when struck": [
        "201,87"
    ],
    "{}% Chance to cast level {} Bone Prison when struck": [
        "201,88"
    ],
    "{}% Chance to cast level {} Summon Resist when struck": [
        "201,89"
    ],
    "{}% Chance to cast level {} Iron Golem when struck": [
        "201,90"
    ],
    "{}% Chance to cast level {} Lower Resist when struck": [
        "201,91"
    ],
    "{}% Chance to cast level {} Poison Nova when struck": [
        "201,92"
    ],
    "{}% Chance to cast level {} Bone Spirit when struck": [
        "201,93"
    ],
    "{}% Chance to cast level {} Fire Golem when struck": [
        "201,94"
    ],
    "{}% Chance to cast level {} Revive when struck": [
        "201,95"
    ],
    "{}% Chance to cast level {} Sacrifice when struck": [
        "201,96"
    ],
    "{}% Chance to cast level {} Smite when struck": [
        "201,97"
    ],
    "{}% Chance to cast level {} Might when struck": [
        "201,98"
    ],
    "{}% Chance to cast level {} Prayer when struck": [
        "201,99"
    ],
    "{}% Chance to cast level {} Resist Fire when struck": [
        "201,100"
    ],
    "{}% Chance to cast level {} Holy Bolt when struck": [
        "201,101"
    ],
    "{}% Chance to cast level {} Holy Fire when struck": [
        "201,102"
    ],
    "{}% Chance to cast level {} Thorns when struck": [
        "201,103"
    ],
    "{}% Chance to cast level {} Defiance when struck": [
        "201,104"
    ],
    "{}% Chance to cast level {} Resist Cold when struck": [
        "201,105"
    ],
    "{}% Chance to cast level {} Zeal when struck": [
        "201,106"
    ],
    "{}% Chance to cast level {} Charge when struck": [
        "201,107"
    ],
    "{}% Chance to cast level {} Blessed Aim when struck": [
        "201,108"
    ],
    "{}% Chance to cast level {} Cleansing when struck": [
        "201,109"
    ],
    "{}% Chance to cast level {} Resist Lightning when struck": [
        "201,110"
    ],
    "{}% Chance to cast level {} Vengeance when struck": [
        "201,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer when struck": [
        "201,112"
    ],
    "{}% Chance to cast level {} Concentration when struck": [
        "201,113"
    ],
    "{}% Chance to cast level {} Holy Freeze when struck": [
        "201,114"
    ],
    "{}% Chance to cast level {} Vigor when struck": [
        "201,115"
    ],
    "{}% Chance to cast level {} Conversion when struck": [
        "201,116"
    ],
    "{}% Chance to cast level {} Holy Shield when struck": [
        "201,117"
    ],
    "{}% Chance to cast level {} Holy Shock when struck": [
        "201,118"
    ],
    "{}% Chance to cast level {} Sanctuary when struck": [
        "201,119"
    ],
    "{}% Chance to cast level {} Meditation when struck": [
        "201,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens when struck": [
        "201,121"
    ],
    "{}% Chance to cast level {} Fanaticism when struck": [
        "201,122"
    ],
    "{}% Chance to cast level {} Conviction when struck": [
        "201,123"
    ],
    "{}% Chance to cast level {} Redemption when struck": [
        "201,124"
    ],
    "{}% Chance to cast level {} Salvation when struck": [
        "201,125"
    ],
    "{}% Chance to cast level {} Bash when struck": [
        "201,126"
    ],
    "{}% Chance to cast level {} Blade Mastery when struck": [
        "201,127"
    ],
    "{}% Chance to cast level {} Axe Mastery when struck": [
        "201,128"
    ],
    "{}% Chance to cast level {} Mace Mastery when struck": [
        "201,129"
    ],
    "{}% Chance to cast level {} Howl when struck": [
        "201,130"
    ],
    "{}% Chance to cast level {} Find Potion when struck": [
        "201,131"
    ],
    "{}% Chance to cast level {} Leap when struck": [
        "201,132"
    ],
    "{}% Chance to cast level {} Double Swing when struck": [
        "201,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery when struck": [
        "201,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery when struck": [
        "201,135"
    ],
    "{}% Chance to cast level {} Spear Mastery when struck": [
        "201,136"
    ],
    "{}% Chance to cast level {} Taunt when struck": [
        "201,137"
    ],
    "{}% Chance to cast level {} Shout when struck": [
        "201,138"
    ],
    "{}% Chance to cast level {} Stun when struck": [
        "201,139"
    ],
    "{}% Chance to cast level {} Double Throw when struck": [
        "201,140"
    ],
    "{}% Chance to cast level {} Increased Stamina when struck": [
        "201,141"
    ],
    "{}% Chance to cast level {} Find Item when struck": [
        "201,142"
    ],
    "{}% Chance to cast level {} Leap Attack when struck": [
        "201,143"
    ],
    "{}% Chance to cast level {} Concentrate when struck": [
        "201,144"
    ],
    "{}% Chance to cast level {} Iron Skin when struck": [
        "201,145"
    ],
    "{}% Chance to cast level {} Battle Cry when struck": [
        "201,146"
    ],
    "{}% Chance to cast level {} Frenzy when struck": [
        "201,147"
    ],
    "{}% Chance to cast level {} Increased Speed when struck": [
        "201,148"
    ],
    "{}% Chance to cast level {} Battle Orders when struck": [
        "201,149"
    ],
    "{}% Chance to cast level {} Grim Ward when struck": [
        "201,150"
    ],
    "{}% Chance to cast level {} Whirlwind when struck": [
        "201,151"
    ],
    "{}% Chance to cast level {} Berserk when struck": [
        "201,152"
    ],
    "{}% Chance to cast level {} Natural Resistance when struck": [
        "201,153"
    ],
    "{}% Chance to cast level {} War Cry when struck": [
        "201,154"
    ],
    "{}% Chance to cast level {} Battle Command when struck": [
        "201,155"
    ],
    "{}% Chance to cast level {} Raven when struck": [
        "201,221"
    ],
    "{}% Chance to cast level {} Poison Creeper when struck": [
        "201,222"
    ],
    "{}% Chance to cast level {} Werewolf when struck": [
        "201,223"
    ],
    "{}% Chance to cast level {} Lycanthropy when struck": [
        "201,224"
    ],
    "{}% Chance to cast level {} Firestorm when struck": [
        "201,225"
    ],
    "{}% Chance to cast level {} Oak Sage when struck": [
        "201,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf when struck": [
        "201,227"
    ],
    "{}% Chance to cast level {} Werebear when struck": [
        "201,228"
    ],
    "{}% Chance to cast level {} Molten Boulder when struck": [
        "201,229"
    ],
    "{}% Chance to cast level {} Arctic Blast when struck": [
        "201,230"
    ],
    "{}% Chance to cast level {} Carrion Vine when struck": [
        "201,231"
    ],
    "{}% Chance to cast level {} Feral Rage when struck": [
        "201,232"
    ],
    "{}% Chance to cast level {} Maul when struck": [
        "201,233"
    ],
    "{}% Chance to cast level {} Fissure when struck": [
        "201,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor when struck": [
        "201,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine when struck": [
        "201,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf when struck": [
        "201,237"
    ],
    "{}% Chance to cast level {} Rabies when struck": [
        "201,238"
    ],
    "{}% Chance to cast level {} Fire Claws when struck": [
        "201,239"
    ],
    "{}% Chance to cast level {} Twister when struck": [
        "201,240"
    ],
    "{}% Chance to cast level {} Solar Creeper when struck": [
        "201,241"
    ],
    "{}% Chance to cast level {} Hunger when struck": [
        "201,242"
    ],
    "{}% Chance to cast level {} Shock Wave when struck": [
        "201,243"
    ],
    "{}% Chance to cast level {} Volcano when struck": [
        "201,244"
    ],
    "{}% Chance to cast level {} Tornado when struck": [
        "201,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs when struck": [
        "201,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly when struck": [
        "201,247"
    ],
    "{}% Chance to cast level {} Fury when struck": [
        "201,248"
    ],
    "{}% Chance to cast level {} Armageddon when struck": [
        "201,249"
    ],
    "{}% Chance to cast level {} Hurricane when struck": [
        "201,250"
    ],
    "{}% Chance to cast level {} Fire Blast when struck": [
        "201,251"
    ],
    "{}% Chance to cast level {} Claw Mastery when struck": [
        "201,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer when struck": [
        "201,253"
    ],
    "{}% Chance to cast level {} Tiger Strike when struck": [
        "201,254"
    ],
    "{}% Chance to cast level {} Dragon Talon when struck": [
        "201,255"
    ],
    "{}% Chance to cast level {} Shock Web when struck": [
        "201,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel when struck": [
        "201,257"
    ],
    "{}% Chance to cast level {} Burst of Speed when struck": [
        "201,258"
    ],
    "{}% Chance to cast level {} Fists of Fire when struck": [
        "201,259"
    ],
    "{}% Chance to cast level {} Dragon Claw when struck": [
        "201,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry when struck": [
        "201,261"
    ],
    "{}% Chance to cast level {} Wake of Fire when struck": [
        "201,262"
    ],
    "{}% Chance to cast level {} Weapon Block when struck": [
        "201,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows when struck": [
        "201,264"
    ],
    "{}% Chance to cast level {} Cobra Strike when struck": [
        "201,265"
    ],
    "{}% Chance to cast level {} Blade Fury when struck": [
        "201,266"
    ],
    "{}% Chance to cast level {} Fade when struck": [
        "201,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior when struck": [
        "201,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder when struck": [
        "201,269"
    ],
    "{}% Chance to cast level {} Dragon Tail when struck": [
        "201,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry when struck": [
        "201,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno when struck": [
        "201,272"
    ],
    "{}% Chance to cast level {} Mind Blast when struck": [
        "201,273"
    ],
    "{}% Chance to cast level {} Blades of Ice when struck": [
        "201,274"
    ],
    "{}% Chance to cast level {} Dragon Flight when struck": [
        "201,275"
    ],
    "{}% Chance to cast level {} Death Sentry when struck": [
        "201,276"
    ],
    "{}% Chance to cast level {} Blade Shield when struck": [
        "201,277"
    ],
    "{}% Chance to cast level {} Venom when struck": [
        "201,278"
    ],
    "{}% Chance to cast level {} Shadow Master when struck": [
        "201,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike when struck": [
        "201,280"
    ],
    "Socketed ({})": [
        "194"
    ],
    "Adds {}-{} Fire Damage": [
        "48",
        "49"
    ],
    "Adds {}-{} Lightning Damage": [
        "50",
        "51"
    ],
    "Adds {}-{} Magic Damage": [
        "52",
        "53"
    ],
    "Adds {}-{} Cold Damage": [
        "54",
        "55"
    ],
    "Adds {}-{} Poison Damage Over {} Seconds": [
        "57",
        "58",
        "59"
    ],
    "Adds {}-{} Damage": [
        "21",
        "22"
    ],
    "+{} Defense (Based on Character Level)": [
        "214"
    ],
    "+{}% Enhanced Defense (Based on Character Level)": [
        "215"
    ],
    "+{} to Life (Based on Character Level)": [
        "216"
    ],
    "+{} to Mana (Based on Character Level)": [
        "217"
    ],
    "+{} to Maximum Damage (Based on Character Level)": [
        "218"
    ],
    "+{}% Enhanced Maximum Damage (Based on Character Level)": [
        "219"
    ],
    "+{} to Strength (Based on Character Level)": [
        "220"
    ],
    "+{} to Dexterity (Based on Character Level)": [
        "221"
    ],
    "+{} to Vitality (Based on Character Level)": [
        "223"
    ],
    "+{} to Attack Rating (Based on Character Level)": [
        "224"
    ],
    "{}% Bonus to Attack Rating (Based on Character Level)": [
        "225"
    ],
    "Cold Resist +{}% (Based on Character Level)": [
        "230"
    ],
    "Fire Resist +{}% (Based on Character Level)": [
        "231"
    ],
    "Lightning Resist +{}% (Based on Character Level)": [
        "232"
    ],
    "Poison Resist +{}% (Based on Character Level)": [
        "233"
    ],
    "Absorbs Cold Damage (Based on Character Level)": [
        "234"
    ],
    "Absorbs Fire Damage (Based on Character Level)": [
        "235"
    ],
    "Attacker Takes Damage of {} (Based on Character Level)": [
        "238"
    ],
    "{}% Extra Gold from Monsters (Based on Character Level)": [
        "239"
    ],
    "{}% Better Chance of Getting Magic Items (Based on Character Level)": [
        "240"
    ],
    "Heal Stamina Plus {}% (Based on Character Level)": [
        "241"
    ],
    "+{} Maximum Stamina (Based on Character Level)": [
        "242"
    ],
    "+{}% Damage to Demons (Based on Character Level)": [
        "243"
    ],
    "+{}% Damage to Undead (Based on Character Level)": [
        "244"
    ],
    "+{} to Attack Rating against Demons (Based on Character Level)": [
        "245"
    ],
    "+{} to Attack Rating against Undead (Based on Character Level)": [
        "246"
    ],
    "{}% Deadly Strike (Based on Character Level)": [
        "250"
    ],
    "Repairs 1 durability in {} seconds": [
        "252"
    ],
    "Replenishes quantity": [
        "253"
    ],
    "Increased Stack Size": [
        "254"
    ],
    "+{} Defense (Increases near [Day/Dusk/Night/Dawn])": [
        "268"
    ],
    "+{}% Enhanced Defense (Increases near [Day/Dusk/Night/Dawn])": [
        "269"
    ],
    "+{} to Life (Increases near [Day/Dusk/Night/Dawn])": [
        "270"
    ],
    "+{} to Mana (Increases near [Day/Dusk/Night/Dawn])": [
        "271"
    ],
    "+{} to Maximum Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "272"
    ],
    "+{}% Enhanced Maximum Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "273"
    ],
    "+{} to Strength (Increases near [Day/Dusk/Night/Dawn])": [
        "274"
    ],
    "+{} to Dexterity (Increases near [Day/Dusk/Night/Dawn])": [
        "275"
    ],
    "+{} to Energy (Increases near [Day/Dusk/Night/Dawn])": [
        "276"
    ],
    "+{} to Vitality (Increases near [Day/Dusk/Night/Dawn])": [
        "277"
    ],
    "+{} to Attack Rating (Increases near [Day/Dusk/Night/Dawn])": [
        "278"
    ],
    "{}% Bonus to Attack Rating (Increases near [Day/Dusk/Night/Dawn])": [
        "279"
    ],
    "+{} to Maximum Cold Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "280"
    ],
    "+{} to Maximum Fire Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "281"
    ],
    "+{} to Maximum Lightning Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "282"
    ],
    "+{} to Maximum Poison Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "283"
    ],
    "Cold Resist +{}% (Increases near [Day/Dusk/Night/Dawn])": [
        "284"
    ],
    "Fire Resist +{}% (Increases near [Day/Dusk/Night/Dawn])": [
        "285"
    ],
    "Lightning Resist +{}% (Increases near [Day/Dusk/Night/Dawn])": [
        "286"
    ],
    "Poison Resist +{}% (Increases near [Day/Dusk/Night/Dawn])": [
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
    "{}% Extra Gold from Monsters (Increases near [Day/Dusk/Night/Dawn])": [
        "292"
    ],
    "{}% Better Chance of Getting Magic Items (Increases near [Day/Dusk/Night/Dawn])": [
        "293"
    ],
    "Heal Stamina Plus {}% (Increases near [Day/Dusk/Night/Dawn])": [
        "294"
    ],
    "+{} Maximum Stamina (Increases near [Day/Dusk/Night/Dawn])": [
        "295"
    ],
    "+{}% Damage to Demons (Increases near [Day/Dusk/Night/Dawn])": [
        "296"
    ],
    "+{}% Damage to Undead (Increases near [Day/Dusk/Night/Dawn])": [
        "297"
    ],
    "+{} to Attack Rating against Demons (Increases near [Day/Dusk/Night/Dawn])": [
        "298"
    ],
    "+{} to Attack Rating against Undead (Increases near [Day/Dusk/Night/Dawn])": [
        "299"
    ],
    "{}% Chance of Crushing Blow (Increases near [Day/Dusk/Night/Dawn])": [
        "300"
    ],
    "{}% Chance of Open Wounds (Increases near [Day/Dusk/Night/Dawn])": [
        "301"
    ],
    "+{} Kick Damage (Increases near [Day/Dusk/Night/Dawn])": [
        "302"
    ],
    "{}% Deadly Strike (Increases near [Day/Dusk/Night/Dawn])": [
        "303"
    ],
    "-{}% to Enemy Fire Resistance": [
        "333"
    ],
    "-{}% to Enemy Lightning Resistance": [
        "334"
    ],
    "-{}% to Enemy Cold Resistance": [
        "335"
    ],
    "-{}% to Enemy Poison Resistance": [
        "336"
    ],
    "Level {} Magic Arrow ({}/{} Charges)": [
        "204,6"
    ],
    "Level {} Fire Arrow ({}/{} Charges)": [
        "204,7"
    ],
    "Level {} Inner Sight ({}/{} Charges)": [
        "204,8"
    ],
    "Level {} Critical Strike ({}/{} Charges)": [
        "204,9"
    ],
    "Level {} Jab ({}/{} Charges)": [
        "204,10"
    ],
    "Level {} Cold Arrow ({}/{} Charges)": [
        "204,11"
    ],
    "Level {} Multiple Shot ({}/{} Charges)": [
        "204,12"
    ],
    "Level {} Dodge ({}/{} Charges)": [
        "204,13"
    ],
    "Level {} Power Strike ({}/{} Charges)": [
        "204,14"
    ],
    "Level {} Poison Javelin ({}/{} Charges)": [
        "204,15"
    ],
    "Level {} Exploding Arrow ({}/{} Charges)": [
        "204,16"
    ],
    "Level {} Slow Missiles ({}/{} Charges)": [
        "204,17"
    ],
    "Level {} Avoid ({}/{} Charges)": [
        "204,18"
    ],
    "Level {} Impale ({}/{} Charges)": [
        "204,19"
    ],
    "Level {} Lightning Bolt ({}/{} Charges)": [
        "204,20"
    ],
    "Level {} Ice Arrow ({}/{} Charges)": [
        "204,21"
    ],
    "Level {} Guided Arrow ({}/{} Charges)": [
        "204,22"
    ],
    "Level {} Penetrate ({}/{} Charges)": [
        "204,23"
    ],
    "Level {} Charged Strike ({}/{} Charges)": [
        "204,24"
    ],
    "Level {} Plague Javelin ({}/{} Charges)": [
        "204,25"
    ],
    "Level {} Strafe ({}/{} Charges)": [
        "204,26"
    ],
    "Level {} Immolation Arrow ({}/{} Charges)": [
        "204,27"
    ],
    "Level {} Decoy ({}/{} Charges)": [
        "204,28"
    ],
    "Level {} Evade ({}/{} Charges)": [
        "204,29"
    ],
    "Level {} Fend ({}/{} Charges)": [
        "204,30"
    ],
    "Level {} Freezing Arrow ({}/{} Charges)": [
        "204,31"
    ],
    "Level {} Valkyrie ({}/{} Charges)": [
        "204,32"
    ],
    "Level {} Pierce ({}/{} Charges)": [
        "204,33"
    ],
    "Level {} Lightning Strike ({}/{} Charges)": [
        "204,34"
    ],
    "Level {} Lightning Fury ({}/{} Charges)": [
        "204,35"
    ],
    "Level {} Fire Bolt ({}/{} Charges)": [
        "204,36"
    ],
    "Level {} Warmth ({}/{} Charges)": [
        "204,37"
    ],
    "Level {} Charged Bolt ({}/{} Charges)": [
        "204,38"
    ],
    "Level {} Ice Bolt ({}/{} Charges)": [
        "204,39"
    ],
    "Level {} Frozen Armor ({}/{} Charges)": [
        "204,40"
    ],
    "Level {} Inferno ({}/{} Charges)": [
        "204,41"
    ],
    "Level {} Static Field ({}/{} Charges)": [
        "204,42"
    ],
    "Level {} Telekinesis ({}/{} Charges)": [
        "204,43"
    ],
    "Level {} Frost Nova ({}/{} Charges)": [
        "204,44"
    ],
    "Level {} Ice Blast ({}/{} Charges)": [
        "204,45"
    ],
    "Level {} Blaze ({}/{} Charges)": [
        "204,46"
    ],
    "Level {} Fire Ball ({}/{} Charges)": [
        "204,47"
    ],
    "Level {} Nova ({}/{} Charges)": [
        "204,48"
    ],
    "Level {} Lightning ({}/{} Charges)": [
        "204,49"
    ],
    "Level {} Shiver Armor ({}/{} Charges)": [
        "204,50"
    ],
    "Level {} Fire Wall ({}/{} Charges)": [
        "204,51"
    ],
    "Level {} Enchant ({}/{} Charges)": [
        "204,52"
    ],
    "Level {} Chain Lightning ({}/{} Charges)": [
        "204,53"
    ],
    "Level {} Teleport ({}/{} Charges)": [
        "204,54"
    ],
    "Level {} Glacial Spike ({}/{} Charges)": [
        "204,55"
    ],
    "Level {} Meteor ({}/{} Charges)": [
        "204,56"
    ],
    "Level {} Thunder Storm ({}/{} Charges)": [
        "204,57"
    ],
    "Level {} Energy Shield ({}/{} Charges)": [
        "204,58"
    ],
    "Level {} Blizzard ({}/{} Charges)": [
        "204,59"
    ],
    "Level {} Chilling Armor ({}/{} Charges)": [
        "204,60"
    ],
    "Level {} Fire Mastery ({}/{} Charges)": [
        "204,61"
    ],
    "Level {} Hydra ({}/{} Charges)": [
        "204,62"
    ],
    "Level {} Lightning Mastery ({}/{} Charges)": [
        "204,63"
    ],
    "Level {} Frozen Orb ({}/{} Charges)": [
        "204,64"
    ],
    "Level {} Cold Mastery ({}/{} Charges)": [
        "204,65"
    ],
    "Level {} Amplify Damage ({}/{} Charges)": [
        "204,66"
    ],
    "Level {} Teeth ({}/{} Charges)": [
        "204,67"
    ],
    "Level {} Bone Armor ({}/{} Charges)": [
        "204,68"
    ],
    "Level {} Skeleton Mastery ({}/{} Charges)": [
        "204,69"
    ],
    "Level {} Raise Skeleton ({}/{} Charges)": [
        "204,70"
    ],
    "Level {} Dim Vision ({}/{} Charges)": [
        "204,71"
    ],
    "Level {} Weaken ({}/{} Charges)": [
        "204,72"
    ],
    "Level {} Poison Dagger ({}/{} Charges)": [
        "204,73"
    ],
    "Level {} Corpse Explosion ({}/{} Charges)": [
        "204,74"
    ],
    "Level {} Clay Golem ({}/{} Charges)": [
        "204,75"
    ],
    "Level {} Iron Maiden ({}/{} Charges)": [
        "204,76"
    ],
    "Level {} Terror ({}/{} Charges)": [
        "204,77"
    ],
    "Level {} Bone Wall ({}/{} Charges)": [
        "204,78"
    ],
    "Level {} Golem Mastery ({}/{} Charges)": [
        "204,79"
    ],
    "Level {} Raise Skeletal Mage ({}/{} Charges)": [
        "204,80"
    ],
    "Level {} Confuse ({}/{} Charges)": [
        "204,81"
    ],
    "Level {} Life Tap ({}/{} Charges)": [
        "204,82"
    ],
    "Level {} Poison Explosion ({}/{} Charges)": [
        "204,83"
    ],
    "Level {} Bone Spear ({}/{} Charges)": [
        "204,84"
    ],
    "Level {} Blood Golem ({}/{} Charges)": [
        "204,85"
    ],
    "Level {} Attract ({}/{} Charges)": [
        "204,86"
    ],
    "Level {} Decrepify ({}/{} Charges)": [
        "204,87"
    ],
    "Level {} Bone Prison ({}/{} Charges)": [
        "204,88"
    ],
    "Level {} Summon Resist ({}/{} Charges)": [
        "204,89"
    ],
    "Level {} Iron Golem ({}/{} Charges)": [
        "204,90"
    ],
    "Level {} Lower Resist ({}/{} Charges)": [
        "204,91"
    ],
    "Level {} Poison Nova ({}/{} Charges)": [
        "204,92"
    ],
    "Level {} Bone Spirit ({}/{} Charges)": [
        "204,93"
    ],
    "Level {} Fire Golem ({}/{} Charges)": [
        "204,94"
    ],
    "Level {} Revive ({}/{} Charges)": [
        "204,95"
    ],
    "Level {} Sacrifice ({}/{} Charges)": [
        "204,96"
    ],
    "Level {} Smite ({}/{} Charges)": [
        "204,97"
    ],
    "Level {} Might ({}/{} Charges)": [
        "204,98"
    ],
    "Level {} Prayer ({}/{} Charges)": [
        "204,99"
    ],
    "Level {} Resist Fire ({}/{} Charges)": [
        "204,100"
    ],
    "Level {} Holy Bolt ({}/{} Charges)": [
        "204,101"
    ],
    "Level {} Holy Fire ({}/{} Charges)": [
        "204,102"
    ],
    "Level {} Thorns ({}/{} Charges)": [
        "204,103"
    ],
    "Level {} Defiance ({}/{} Charges)": [
        "204,104"
    ],
    "Level {} Resist Cold ({}/{} Charges)": [
        "204,105"
    ],
    "Level {} Zeal ({}/{} Charges)": [
        "204,106"
    ],
    "Level {} Charge ({}/{} Charges)": [
        "204,107"
    ],
    "Level {} Blessed Aim ({}/{} Charges)": [
        "204,108"
    ],
    "Level {} Cleansing ({}/{} Charges)": [
        "204,109"
    ],
    "Level {} Resist Lightning ({}/{} Charges)": [
        "204,110"
    ],
    "Level {} Vengeance ({}/{} Charges)": [
        "204,111"
    ],
    "Level {} Blessed Hammer ({}/{} Charges)": [
        "204,112"
    ],
    "Level {} Concentration ({}/{} Charges)": [
        "204,113"
    ],
    "Level {} Holy Freeze ({}/{} Charges)": [
        "204,114"
    ],
    "Level {} Vigor ({}/{} Charges)": [
        "204,115"
    ],
    "Level {} Conversion ({}/{} Charges)": [
        "204,116"
    ],
    "Level {} Holy Shield ({}/{} Charges)": [
        "204,117"
    ],
    "Level {} Holy Shock ({}/{} Charges)": [
        "204,118"
    ],
    "Level {} Sanctuary ({}/{} Charges)": [
        "204,119"
    ],
    "Level {} Meditation ({}/{} Charges)": [
        "204,120"
    ],
    "Level {} Fist of the Heavens ({}/{} Charges)": [
        "204,121"
    ],
    "Level {} Fanaticism ({}/{} Charges)": [
        "204,122"
    ],
    "Level {} Conviction ({}/{} Charges)": [
        "204,123"
    ],
    "Level {} Redemption ({}/{} Charges)": [
        "204,124"
    ],
    "Level {} Salvation ({}/{} Charges)": [
        "204,125"
    ],
    "Level {} Bash ({}/{} Charges)": [
        "204,126"
    ],
    "Level {} Blade Mastery ({}/{} Charges)": [
        "204,127"
    ],
    "Level {} Axe Mastery ({}/{} Charges)": [
        "204,128"
    ],
    "Level {} Mace Mastery ({}/{} Charges)": [
        "204,129"
    ],
    "Level {} Howl ({}/{} Charges)": [
        "204,130"
    ],
    "Level {} Find Potion ({}/{} Charges)": [
        "204,131"
    ],
    "Level {} Leap ({}/{} Charges)": [
        "204,132"
    ],
    "Level {} Double Swing ({}/{} Charges)": [
        "204,133"
    ],
    "Level {} Polearm Mastery ({}/{} Charges)": [
        "204,134"
    ],
    "Level {} Throwing Mastery ({}/{} Charges)": [
        "204,135"
    ],
    "Level {} Spear Mastery ({}/{} Charges)": [
        "204,136"
    ],
    "Level {} Taunt ({}/{} Charges)": [
        "204,137"
    ],
    "Level {} Shout ({}/{} Charges)": [
        "204,138"
    ],
    "Level {} Stun ({}/{} Charges)": [
        "204,139"
    ],
    "Level {} Double Throw ({}/{} Charges)": [
        "204,140"
    ],
    "Level {} Increased Stamina ({}/{} Charges)": [
        "204,141"
    ],
    "Level {} Find Item ({}/{} Charges)": [
        "204,142"
    ],
    "Level {} Leap Attack ({}/{} Charges)": [
        "204,143"
    ],
    "Level {} Concentrate ({}/{} Charges)": [
        "204,144"
    ],
    "Level {} Iron Skin ({}/{} Charges)": [
        "204,145"
    ],
    "Level {} Battle Cry ({}/{} Charges)": [
        "204,146"
    ],
    "Level {} Frenzy ({}/{} Charges)": [
        "204,147"
    ],
    "Level {} Increased Speed ({}/{} Charges)": [
        "204,148"
    ],
    "Level {} Battle Orders ({}/{} Charges)": [
        "204,149"
    ],
    "Level {} Grim Ward ({}/{} Charges)": [
        "204,150"
    ],
    "Level {} Whirlwind ({}/{} Charges)": [
        "204,151"
    ],
    "Level {} Berserk ({}/{} Charges)": [
        "204,152"
    ],
    "Level {} Natural Resistance ({}/{} Charges)": [
        "204,153"
    ],
    "Level {} War Cry ({}/{} Charges)": [
        "204,154"
    ],
    "Level {} Battle Command ({}/{} Charges)": [
        "204,155"
    ],
    "Level {} Raven ({}/{} Charges)": [
        "204,221"
    ],
    "Level {} Poison Creeper ({}/{} Charges)": [
        "204,222"
    ],
    "Level {} Werewolf ({}/{} Charges)": [
        "204,223"
    ],
    "Level {} Lycanthropy ({}/{} Charges)": [
        "204,224"
    ],
    "Level {} Firestorm ({}/{} Charges)": [
        "204,225"
    ],
    "Level {} Oak Sage ({}/{} Charges)": [
        "204,226"
    ],
    "Level {} Summon Spirit Wolf ({}/{} Charges)": [
        "204,227"
    ],
    "Level {} Werebear ({}/{} Charges)": [
        "204,228"
    ],
    "Level {} Molten Boulder ({}/{} Charges)": [
        "204,229"
    ],
    "Level {} Arctic Blast ({}/{} Charges)": [
        "204,230"
    ],
    "Level {} Carrion Vine ({}/{} Charges)": [
        "204,231"
    ],
    "Level {} Feral Rage ({}/{} Charges)": [
        "204,232"
    ],
    "Level {} Maul ({}/{} Charges)": [
        "204,233"
    ],
    "Level {} Fissure ({}/{} Charges)": [
        "204,234"
    ],
    "Level {} Cyclone Armor ({}/{} Charges)": [
        "204,235"
    ],
    "Level {} Heart of Wolverine ({}/{} Charges)": [
        "204,236"
    ],
    "Level {} Summon Dire Wolf ({}/{} Charges)": [
        "204,237"
    ],
    "Level {} Rabies ({}/{} Charges)": [
        "204,238"
    ],
    "Level {} Fire Claws ({}/{} Charges)": [
        "204,239"
    ],
    "Level {} Twister ({}/{} Charges)": [
        "204,240"
    ],
    "Level {} Solar Creeper ({}/{} Charges)": [
        "204,241"
    ],
    "Level {} Hunger ({}/{} Charges)": [
        "204,242"
    ],
    "Level {} Shock Wave ({}/{} Charges)": [
        "204,243"
    ],
    "Level {} Volcano ({}/{} Charges)": [
        "204,244"
    ],
    "Level {} Tornado ({}/{} Charges)": [
        "204,245"
    ],
    "Level {} Spirit of Barbs ({}/{} Charges)": [
        "204,246"
    ],
    "Level {} Summon Grizzly ({}/{} Charges)": [
        "204,247"
    ],
    "Level {} Fury ({}/{} Charges)": [
        "204,248"
    ],
    "Level {} Armageddon ({}/{} Charges)": [
        "204,249"
    ],
    "Level {} Hurricane ({}/{} Charges)": [
        "204,250"
    ],
    "Level {} Fire Blast ({}/{} Charges)": [
        "204,251"
    ],
    "Level {} Claw Mastery ({}/{} Charges)": [
        "204,252"
    ],
    "Level {} Psychic Hammer ({}/{} Charges)": [
        "204,253"
    ],
    "Level {} Tiger Strike ({}/{} Charges)": [
        "204,254"
    ],
    "Level {} Dragon Talon ({}/{} Charges)": [
        "204,255"
    ],
    "Level {} Shock Web ({}/{} Charges)": [
        "204,256"
    ],
    "Level {} Blade Sentinel ({}/{} Charges)": [
        "204,257"
    ],
    "Level {} Burst of Speed ({}/{} Charges)": [
        "204,258"
    ],
    "Level {} Fists of Fire ({}/{} Charges)": [
        "204,259"
    ],
    "Level {} Dragon Claw ({}/{} Charges)": [
        "204,260"
    ],
    "Level {} Charged Bolt Sentry ({}/{} Charges)": [
        "204,261"
    ],
    "Level {} Wake of Fire ({}/{} Charges)": [
        "204,262"
    ],
    "Level {} Weapon Block ({}/{} Charges)": [
        "204,263"
    ],
    "Level {} Cloak of Shadows ({}/{} Charges)": [
        "204,264"
    ],
    "Level {} Cobra Strike ({}/{} Charges)": [
        "204,265"
    ],
    "Level {} Blade Fury ({}/{} Charges)": [
        "204,266"
    ],
    "Level {} Fade ({}/{} Charges)": [
        "204,267"
    ],
    "Level {} Shadow Warrior ({}/{} Charges)": [
        "204,268"
    ],
    "Level {} Claws of Thunder ({}/{} Charges)": [
        "204,269"
    ],
    "Level {} Dragon Tail ({}/{} Charges)": [
        "204,270"
    ],
    "Level {} Lightning Sentry ({}/{} Charges)": [
        "204,271"
    ],
    "Level {} Wake of Inferno ({}/{} Charges)": [
        "204,272"
    ],
    "Level {} Mind Blast ({}/{} Charges)": [
        "204,273"
    ],
    "Level {} Blades of Ice ({}/{} Charges)": [
        "204,274"
    ],
    "Level {} Dragon Flight ({}/{} Charges)": [
        "204,275"
    ],
    "Level {} Death Sentry ({}/{} Charges)": [
        "204,276"
    ],
    "Level {} Blade Shield ({}/{} Charges)": [
        "204,277"
    ],
    "Level {} Venom ({}/{} Charges)": [
        "204,278"
    ],
    "Level {} Shadow Master ({}/{} Charges)": [
        "204,279"
    ],
    "Level {} Phoenix Strike ({}/{} Charges)": [
        "204,280"
    ],
    "+{}% to Fire Skill Damage": [
        "329"
    ],
    "+{}% to Lightning Skill Damage": [
        "330"
    ],
    "+{}% to Cold Skill Damage": [
        "331"
    ],
    "+{}% to Poison Skill Damage": [
        "332"
    ],
    "Adds {}-{} Fire/Lightning/Cold Damage": [
        "48",
        "49"
    ],
    "+{} to all Attributes": [
        "420",
        "0",
        "2",
        "3",
        "1"
    ],
    "+{}% to Experience Gained": [
        "85"
    ],
    "+{} Life after each Kill": [
        "86"
    ],
    "Reduces all Vendor Prices {}%": [
        "87"
    ],
    "Slain Monsters Rest in Peace": [
        "108"
    ],
    "{}% Chance to cast level {} Magic Arrow when you Kill an Enemy": [
        "196,6"
    ],
    "{}% Chance to cast level {} Fire Arrow when you Kill an Enemy": [
        "196,7"
    ],
    "{}% Chance to cast level {} Inner Sight when you Kill an Enemy": [
        "196,8"
    ],
    "{}% Chance to cast level {} Critical Strike when you Kill an Enemy": [
        "196,9"
    ],
    "{}% Chance to cast level {} Jab when you Kill an Enemy": [
        "196,10"
    ],
    "{}% Chance to cast level {} Cold Arrow when you Kill an Enemy": [
        "196,11"
    ],
    "{}% Chance to cast level {} Multiple Shot when you Kill an Enemy": [
        "196,12"
    ],
    "{}% Chance to cast level {} Dodge when you Kill an Enemy": [
        "196,13"
    ],
    "{}% Chance to cast level {} Power Strike when you Kill an Enemy": [
        "196,14"
    ],
    "{}% Chance to cast level {} Poison Javelin when you Kill an Enemy": [
        "196,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow when you Kill an Enemy": [
        "196,16"
    ],
    "{}% Chance to cast level {} Slow Missiles when you Kill an Enemy": [
        "196,17"
    ],
    "{}% Chance to cast level {} Avoid when you Kill an Enemy": [
        "196,18"
    ],
    "{}% Chance to cast level {} Impale when you Kill an Enemy": [
        "196,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt when you Kill an Enemy": [
        "196,20"
    ],
    "{}% Chance to cast level {} Ice Arrow when you Kill an Enemy": [
        "196,21"
    ],
    "{}% Chance to cast level {} Guided Arrow when you Kill an Enemy": [
        "196,22"
    ],
    "{}% Chance to cast level {} Penetrate when you Kill an Enemy": [
        "196,23"
    ],
    "{}% Chance to cast level {} Charged Strike when you Kill an Enemy": [
        "196,24"
    ],
    "{}% Chance to cast level {} Plague Javelin when you Kill an Enemy": [
        "196,25"
    ],
    "{}% Chance to cast level {} Strafe when you Kill an Enemy": [
        "196,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow when you Kill an Enemy": [
        "196,27"
    ],
    "{}% Chance to cast level {} Decoy when you Kill an Enemy": [
        "196,28"
    ],
    "{}% Chance to cast level {} Evade when you Kill an Enemy": [
        "196,29"
    ],
    "{}% Chance to cast level {} Fend when you Kill an Enemy": [
        "196,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow when you Kill an Enemy": [
        "196,31"
    ],
    "{}% Chance to cast level {} Valkyrie when you Kill an Enemy": [
        "196,32"
    ],
    "{}% Chance to cast level {} Pierce when you Kill an Enemy": [
        "196,33"
    ],
    "{}% Chance to cast level {} Lightning Strike when you Kill an Enemy": [
        "196,34"
    ],
    "{}% Chance to cast level {} Lightning Fury when you Kill an Enemy": [
        "196,35"
    ],
    "{}% Chance to cast level {} Fire Bolt when you Kill an Enemy": [
        "196,36"
    ],
    "{}% Chance to cast level {} Warmth when you Kill an Enemy": [
        "196,37"
    ],
    "{}% Chance to cast level {} Charged Bolt when you Kill an Enemy": [
        "196,38"
    ],
    "{}% Chance to cast level {} Ice Bolt when you Kill an Enemy": [
        "196,39"
    ],
    "{}% Chance to cast level {} Frozen Armor when you Kill an Enemy": [
        "196,40"
    ],
    "{}% Chance to cast level {} Inferno when you Kill an Enemy": [
        "196,41"
    ],
    "{}% Chance to cast level {} Static Field when you Kill an Enemy": [
        "196,42"
    ],
    "{}% Chance to cast level {} Telekinesis when you Kill an Enemy": [
        "196,43"
    ],
    "{}% Chance to cast level {} Frost Nova when you Kill an Enemy": [
        "196,44"
    ],
    "{}% Chance to cast level {} Ice Blast when you Kill an Enemy": [
        "196,45"
    ],
    "{}% Chance to cast level {} Blaze when you Kill an Enemy": [
        "196,46"
    ],
    "{}% Chance to cast level {} Fire Ball when you Kill an Enemy": [
        "196,47"
    ],
    "{}% Chance to cast level {} Nova when you Kill an Enemy": [
        "196,48"
    ],
    "{}% Chance to cast level {} Lightning when you Kill an Enemy": [
        "196,49"
    ],
    "{}% Chance to cast level {} Shiver Armor when you Kill an Enemy": [
        "196,50"
    ],
    "{}% Chance to cast level {} Fire Wall when you Kill an Enemy": [
        "196,51"
    ],
    "{}% Chance to cast level {} Enchant when you Kill an Enemy": [
        "196,52"
    ],
    "{}% Chance to cast level {} Chain Lightning when you Kill an Enemy": [
        "196,53"
    ],
    "{}% Chance to cast level {} Teleport when you Kill an Enemy": [
        "196,54"
    ],
    "{}% Chance to cast level {} Glacial Spike when you Kill an Enemy": [
        "196,55"
    ],
    "{}% Chance to cast level {} Meteor when you Kill an Enemy": [
        "196,56"
    ],
    "{}% Chance to cast level {} Thunder Storm when you Kill an Enemy": [
        "196,57"
    ],
    "{}% Chance to cast level {} Energy Shield when you Kill an Enemy": [
        "196,58"
    ],
    "{}% Chance to cast level {} Blizzard when you Kill an Enemy": [
        "196,59"
    ],
    "{}% Chance to cast level {} Chilling Armor when you Kill an Enemy": [
        "196,60"
    ],
    "{}% Chance to cast level {} Fire Mastery when you Kill an Enemy": [
        "196,61"
    ],
    "{}% Chance to cast level {} Hydra when you Kill an Enemy": [
        "196,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery when you Kill an Enemy": [
        "196,63"
    ],
    "{}% Chance to cast level {} Frozen Orb when you Kill an Enemy": [
        "196,64"
    ],
    "{}% Chance to cast level {} Cold Mastery when you Kill an Enemy": [
        "196,65"
    ],
    "{}% Chance to cast level {} Amplify Damage when you Kill an Enemy": [
        "196,66"
    ],
    "{}% Chance to cast level {} Teeth when you Kill an Enemy": [
        "196,67"
    ],
    "{}% Chance to cast level {} Bone Armor when you Kill an Enemy": [
        "196,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery when you Kill an Enemy": [
        "196,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton when you Kill an Enemy": [
        "196,70"
    ],
    "{}% Chance to cast level {} Dim Vision when you Kill an Enemy": [
        "196,71"
    ],
    "{}% Chance to cast level {} Weaken when you Kill an Enemy": [
        "196,72"
    ],
    "{}% Chance to cast level {} Poison Dagger when you Kill an Enemy": [
        "196,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion when you Kill an Enemy": [
        "196,74"
    ],
    "{}% Chance to cast level {} Clay Golem when you Kill an Enemy": [
        "196,75"
    ],
    "{}% Chance to cast level {} Iron Maiden when you Kill an Enemy": [
        "196,76"
    ],
    "{}% Chance to cast level {} Terror when you Kill an Enemy": [
        "196,77"
    ],
    "{}% Chance to cast level {} Bone Wall when you Kill an Enemy": [
        "196,78"
    ],
    "{}% Chance to cast level {} Golem Mastery when you Kill an Enemy": [
        "196,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage when you Kill an Enemy": [
        "196,80"
    ],
    "{}% Chance to cast level {} Confuse when you Kill an Enemy": [
        "196,81"
    ],
    "{}% Chance to cast level {} Life Tap when you Kill an Enemy": [
        "196,82"
    ],
    "{}% Chance to cast level {} Poison Explosion when you Kill an Enemy": [
        "196,83"
    ],
    "{}% Chance to cast level {} Bone Spear when you Kill an Enemy": [
        "196,84"
    ],
    "{}% Chance to cast level {} Blood Golem when you Kill an Enemy": [
        "196,85"
    ],
    "{}% Chance to cast level {} Attract when you Kill an Enemy": [
        "196,86"
    ],
    "{}% Chance to cast level {} Decrepify when you Kill an Enemy": [
        "196,87"
    ],
    "{}% Chance to cast level {} Bone Prison when you Kill an Enemy": [
        "196,88"
    ],
    "{}% Chance to cast level {} Summon Resist when you Kill an Enemy": [
        "196,89"
    ],
    "{}% Chance to cast level {} Iron Golem when you Kill an Enemy": [
        "196,90"
    ],
    "{}% Chance to cast level {} Lower Resist when you Kill an Enemy": [
        "196,91"
    ],
    "{}% Chance to cast level {} Poison Nova when you Kill an Enemy": [
        "196,92"
    ],
    "{}% Chance to cast level {} Bone Spirit when you Kill an Enemy": [
        "196,93"
    ],
    "{}% Chance to cast level {} Fire Golem when you Kill an Enemy": [
        "196,94"
    ],
    "{}% Chance to cast level {} Revive when you Kill an Enemy": [
        "196,95"
    ],
    "{}% Chance to cast level {} Sacrifice when you Kill an Enemy": [
        "196,96"
    ],
    "{}% Chance to cast level {} Smite when you Kill an Enemy": [
        "196,97"
    ],
    "{}% Chance to cast level {} Might when you Kill an Enemy": [
        "196,98"
    ],
    "{}% Chance to cast level {} Prayer when you Kill an Enemy": [
        "196,99"
    ],
    "{}% Chance to cast level {} Resist Fire when you Kill an Enemy": [
        "196,100"
    ],
    "{}% Chance to cast level {} Holy Bolt when you Kill an Enemy": [
        "196,101"
    ],
    "{}% Chance to cast level {} Holy Fire when you Kill an Enemy": [
        "196,102"
    ],
    "{}% Chance to cast level {} Thorns when you Kill an Enemy": [
        "196,103"
    ],
    "{}% Chance to cast level {} Defiance when you Kill an Enemy": [
        "196,104"
    ],
    "{}% Chance to cast level {} Resist Cold when you Kill an Enemy": [
        "196,105"
    ],
    "{}% Chance to cast level {} Zeal when you Kill an Enemy": [
        "196,106"
    ],
    "{}% Chance to cast level {} Charge when you Kill an Enemy": [
        "196,107"
    ],
    "{}% Chance to cast level {} Blessed Aim when you Kill an Enemy": [
        "196,108"
    ],
    "{}% Chance to cast level {} Cleansing when you Kill an Enemy": [
        "196,109"
    ],
    "{}% Chance to cast level {} Resist Lightning when you Kill an Enemy": [
        "196,110"
    ],
    "{}% Chance to cast level {} Vengeance when you Kill an Enemy": [
        "196,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer when you Kill an Enemy": [
        "196,112"
    ],
    "{}% Chance to cast level {} Concentration when you Kill an Enemy": [
        "196,113"
    ],
    "{}% Chance to cast level {} Holy Freeze when you Kill an Enemy": [
        "196,114"
    ],
    "{}% Chance to cast level {} Vigor when you Kill an Enemy": [
        "196,115"
    ],
    "{}% Chance to cast level {} Conversion when you Kill an Enemy": [
        "196,116"
    ],
    "{}% Chance to cast level {} Holy Shield when you Kill an Enemy": [
        "196,117"
    ],
    "{}% Chance to cast level {} Holy Shock when you Kill an Enemy": [
        "196,118"
    ],
    "{}% Chance to cast level {} Sanctuary when you Kill an Enemy": [
        "196,119"
    ],
    "{}% Chance to cast level {} Meditation when you Kill an Enemy": [
        "196,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens when you Kill an Enemy": [
        "196,121"
    ],
    "{}% Chance to cast level {} Fanaticism when you Kill an Enemy": [
        "196,122"
    ],
    "{}% Chance to cast level {} Conviction when you Kill an Enemy": [
        "196,123"
    ],
    "{}% Chance to cast level {} Redemption when you Kill an Enemy": [
        "196,124"
    ],
    "{}% Chance to cast level {} Salvation when you Kill an Enemy": [
        "196,125"
    ],
    "{}% Chance to cast level {} Bash when you Kill an Enemy": [
        "196,126"
    ],
    "{}% Chance to cast level {} Blade Mastery when you Kill an Enemy": [
        "196,127"
    ],
    "{}% Chance to cast level {} Axe Mastery when you Kill an Enemy": [
        "196,128"
    ],
    "{}% Chance to cast level {} Mace Mastery when you Kill an Enemy": [
        "196,129"
    ],
    "{}% Chance to cast level {} Howl when you Kill an Enemy": [
        "196,130"
    ],
    "{}% Chance to cast level {} Find Potion when you Kill an Enemy": [
        "196,131"
    ],
    "{}% Chance to cast level {} Leap when you Kill an Enemy": [
        "196,132"
    ],
    "{}% Chance to cast level {} Double Swing when you Kill an Enemy": [
        "196,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery when you Kill an Enemy": [
        "196,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery when you Kill an Enemy": [
        "196,135"
    ],
    "{}% Chance to cast level {} Spear Mastery when you Kill an Enemy": [
        "196,136"
    ],
    "{}% Chance to cast level {} Taunt when you Kill an Enemy": [
        "196,137"
    ],
    "{}% Chance to cast level {} Shout when you Kill an Enemy": [
        "196,138"
    ],
    "{}% Chance to cast level {} Stun when you Kill an Enemy": [
        "196,139"
    ],
    "{}% Chance to cast level {} Double Throw when you Kill an Enemy": [
        "196,140"
    ],
    "{}% Chance to cast level {} Increased Stamina when you Kill an Enemy": [
        "196,141"
    ],
    "{}% Chance to cast level {} Find Item when you Kill an Enemy": [
        "196,142"
    ],
    "{}% Chance to cast level {} Leap Attack when you Kill an Enemy": [
        "196,143"
    ],
    "{}% Chance to cast level {} Concentrate when you Kill an Enemy": [
        "196,144"
    ],
    "{}% Chance to cast level {} Iron Skin when you Kill an Enemy": [
        "196,145"
    ],
    "{}% Chance to cast level {} Battle Cry when you Kill an Enemy": [
        "196,146"
    ],
    "{}% Chance to cast level {} Frenzy when you Kill an Enemy": [
        "196,147"
    ],
    "{}% Chance to cast level {} Increased Speed when you Kill an Enemy": [
        "196,148"
    ],
    "{}% Chance to cast level {} Battle Orders when you Kill an Enemy": [
        "196,149"
    ],
    "{}% Chance to cast level {} Grim Ward when you Kill an Enemy": [
        "196,150"
    ],
    "{}% Chance to cast level {} Whirlwind when you Kill an Enemy": [
        "196,151"
    ],
    "{}% Chance to cast level {} Berserk when you Kill an Enemy": [
        "196,152"
    ],
    "{}% Chance to cast level {} Natural Resistance when you Kill an Enemy": [
        "196,153"
    ],
    "{}% Chance to cast level {} War Cry when you Kill an Enemy": [
        "196,154"
    ],
    "{}% Chance to cast level {} Battle Command when you Kill an Enemy": [
        "196,155"
    ],
    "{}% Chance to cast level {} Raven when you Kill an Enemy": [
        "196,221"
    ],
    "{}% Chance to cast level {} Poison Creeper when you Kill an Enemy": [
        "196,222"
    ],
    "{}% Chance to cast level {} Werewolf when you Kill an Enemy": [
        "196,223"
    ],
    "{}% Chance to cast level {} Lycanthropy when you Kill an Enemy": [
        "196,224"
    ],
    "{}% Chance to cast level {} Firestorm when you Kill an Enemy": [
        "196,225"
    ],
    "{}% Chance to cast level {} Oak Sage when you Kill an Enemy": [
        "196,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf when you Kill an Enemy": [
        "196,227"
    ],
    "{}% Chance to cast level {} Werebear when you Kill an Enemy": [
        "196,228"
    ],
    "{}% Chance to cast level {} Molten Boulder when you Kill an Enemy": [
        "196,229"
    ],
    "{}% Chance to cast level {} Arctic Blast when you Kill an Enemy": [
        "196,230"
    ],
    "{}% Chance to cast level {} Carrion Vine when you Kill an Enemy": [
        "196,231"
    ],
    "{}% Chance to cast level {} Feral Rage when you Kill an Enemy": [
        "196,232"
    ],
    "{}% Chance to cast level {} Maul when you Kill an Enemy": [
        "196,233"
    ],
    "{}% Chance to cast level {} Fissure when you Kill an Enemy": [
        "196,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor when you Kill an Enemy": [
        "196,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine when you Kill an Enemy": [
        "196,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf when you Kill an Enemy": [
        "196,237"
    ],
    "{}% Chance to cast level {} Rabies when you Kill an Enemy": [
        "196,238"
    ],
    "{}% Chance to cast level {} Fire Claws when you Kill an Enemy": [
        "196,239"
    ],
    "{}% Chance to cast level {} Twister when you Kill an Enemy": [
        "196,240"
    ],
    "{}% Chance to cast level {} Solar Creeper when you Kill an Enemy": [
        "196,241"
    ],
    "{}% Chance to cast level {} Hunger when you Kill an Enemy": [
        "196,242"
    ],
    "{}% Chance to cast level {} Shock Wave when you Kill an Enemy": [
        "196,243"
    ],
    "{}% Chance to cast level {} Volcano when you Kill an Enemy": [
        "196,244"
    ],
    "{}% Chance to cast level {} Tornado when you Kill an Enemy": [
        "196,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs when you Kill an Enemy": [
        "196,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly when you Kill an Enemy": [
        "196,247"
    ],
    "{}% Chance to cast level {} Fury when you Kill an Enemy": [
        "196,248"
    ],
    "{}% Chance to cast level {} Armageddon when you Kill an Enemy": [
        "196,249"
    ],
    "{}% Chance to cast level {} Hurricane when you Kill an Enemy": [
        "196,250"
    ],
    "{}% Chance to cast level {} Fire Blast when you Kill an Enemy": [
        "196,251"
    ],
    "{}% Chance to cast level {} Claw Mastery when you Kill an Enemy": [
        "196,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer when you Kill an Enemy": [
        "196,253"
    ],
    "{}% Chance to cast level {} Tiger Strike when you Kill an Enemy": [
        "196,254"
    ],
    "{}% Chance to cast level {} Dragon Talon when you Kill an Enemy": [
        "196,255"
    ],
    "{}% Chance to cast level {} Shock Web when you Kill an Enemy": [
        "196,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel when you Kill an Enemy": [
        "196,257"
    ],
    "{}% Chance to cast level {} Burst of Speed when you Kill an Enemy": [
        "196,258"
    ],
    "{}% Chance to cast level {} Fists of Fire when you Kill an Enemy": [
        "196,259"
    ],
    "{}% Chance to cast level {} Dragon Claw when you Kill an Enemy": [
        "196,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry when you Kill an Enemy": [
        "196,261"
    ],
    "{}% Chance to cast level {} Wake of Fire when you Kill an Enemy": [
        "196,262"
    ],
    "{}% Chance to cast level {} Weapon Block when you Kill an Enemy": [
        "196,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows when you Kill an Enemy": [
        "196,264"
    ],
    "{}% Chance to cast level {} Cobra Strike when you Kill an Enemy": [
        "196,265"
    ],
    "{}% Chance to cast level {} Blade Fury when you Kill an Enemy": [
        "196,266"
    ],
    "{}% Chance to cast level {} Fade when you Kill an Enemy": [
        "196,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior when you Kill an Enemy": [
        "196,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder when you Kill an Enemy": [
        "196,269"
    ],
    "{}% Chance to cast level {} Dragon Tail when you Kill an Enemy": [
        "196,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry when you Kill an Enemy": [
        "196,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno when you Kill an Enemy": [
        "196,272"
    ],
    "{}% Chance to cast level {} Mind Blast when you Kill an Enemy": [
        "196,273"
    ],
    "{}% Chance to cast level {} Blades of Ice when you Kill an Enemy": [
        "196,274"
    ],
    "{}% Chance to cast level {} Dragon Flight when you Kill an Enemy": [
        "196,275"
    ],
    "{}% Chance to cast level {} Death Sentry when you Kill an Enemy": [
        "196,276"
    ],
    "{}% Chance to cast level {} Blade Shield when you Kill an Enemy": [
        "196,277"
    ],
    "{}% Chance to cast level {} Venom when you Kill an Enemy": [
        "196,278"
    ],
    "{}% Chance to cast level {} Shadow Master when you Kill an Enemy": [
        "196,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike when you Kill an Enemy": [
        "196,280"
    ],
    "{}% Chance to cast level {} Magic Arrow when you Die": [
        "197,6"
    ],
    "{}% Chance to cast level {} Fire Arrow when you Die": [
        "197,7"
    ],
    "{}% Chance to cast level {} Inner Sight when you Die": [
        "197,8"
    ],
    "{}% Chance to cast level {} Critical Strike when you Die": [
        "197,9"
    ],
    "{}% Chance to cast level {} Jab when you Die": [
        "197,10"
    ],
    "{}% Chance to cast level {} Cold Arrow when you Die": [
        "197,11"
    ],
    "{}% Chance to cast level {} Multiple Shot when you Die": [
        "197,12"
    ],
    "{}% Chance to cast level {} Dodge when you Die": [
        "197,13"
    ],
    "{}% Chance to cast level {} Power Strike when you Die": [
        "197,14"
    ],
    "{}% Chance to cast level {} Poison Javelin when you Die": [
        "197,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow when you Die": [
        "197,16"
    ],
    "{}% Chance to cast level {} Slow Missiles when you Die": [
        "197,17"
    ],
    "{}% Chance to cast level {} Avoid when you Die": [
        "197,18"
    ],
    "{}% Chance to cast level {} Impale when you Die": [
        "197,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt when you Die": [
        "197,20"
    ],
    "{}% Chance to cast level {} Ice Arrow when you Die": [
        "197,21"
    ],
    "{}% Chance to cast level {} Guided Arrow when you Die": [
        "197,22"
    ],
    "{}% Chance to cast level {} Penetrate when you Die": [
        "197,23"
    ],
    "{}% Chance to cast level {} Charged Strike when you Die": [
        "197,24"
    ],
    "{}% Chance to cast level {} Plague Javelin when you Die": [
        "197,25"
    ],
    "{}% Chance to cast level {} Strafe when you Die": [
        "197,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow when you Die": [
        "197,27"
    ],
    "{}% Chance to cast level {} Decoy when you Die": [
        "197,28"
    ],
    "{}% Chance to cast level {} Evade when you Die": [
        "197,29"
    ],
    "{}% Chance to cast level {} Fend when you Die": [
        "197,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow when you Die": [
        "197,31"
    ],
    "{}% Chance to cast level {} Valkyrie when you Die": [
        "197,32"
    ],
    "{}% Chance to cast level {} Pierce when you Die": [
        "197,33"
    ],
    "{}% Chance to cast level {} Lightning Strike when you Die": [
        "197,34"
    ],
    "{}% Chance to cast level {} Lightning Fury when you Die": [
        "197,35"
    ],
    "{}% Chance to cast level {} Fire Bolt when you Die": [
        "197,36"
    ],
    "{}% Chance to cast level {} Warmth when you Die": [
        "197,37"
    ],
    "{}% Chance to cast level {} Charged Bolt when you Die": [
        "197,38"
    ],
    "{}% Chance to cast level {} Ice Bolt when you Die": [
        "197,39"
    ],
    "{}% Chance to cast level {} Frozen Armor when you Die": [
        "197,40"
    ],
    "{}% Chance to cast level {} Inferno when you Die": [
        "197,41"
    ],
    "{}% Chance to cast level {} Static Field when you Die": [
        "197,42"
    ],
    "{}% Chance to cast level {} Telekinesis when you Die": [
        "197,43"
    ],
    "{}% Chance to cast level {} Frost Nova when you Die": [
        "197,44"
    ],
    "{}% Chance to cast level {} Ice Blast when you Die": [
        "197,45"
    ],
    "{}% Chance to cast level {} Blaze when you Die": [
        "197,46"
    ],
    "{}% Chance to cast level {} Fire Ball when you Die": [
        "197,47"
    ],
    "{}% Chance to cast level {} Nova when you Die": [
        "197,48"
    ],
    "{}% Chance to cast level {} Lightning when you Die": [
        "197,49"
    ],
    "{}% Chance to cast level {} Shiver Armor when you Die": [
        "197,50"
    ],
    "{}% Chance to cast level {} Fire Wall when you Die": [
        "197,51"
    ],
    "{}% Chance to cast level {} Enchant when you Die": [
        "197,52"
    ],
    "{}% Chance to cast level {} Chain Lightning when you Die": [
        "197,53"
    ],
    "{}% Chance to cast level {} Teleport when you Die": [
        "197,54"
    ],
    "{}% Chance to cast level {} Glacial Spike when you Die": [
        "197,55"
    ],
    "{}% Chance to cast level {} Meteor when you Die": [
        "197,56"
    ],
    "{}% Chance to cast level {} Thunder Storm when you Die": [
        "197,57"
    ],
    "{}% Chance to cast level {} Energy Shield when you Die": [
        "197,58"
    ],
    "{}% Chance to cast level {} Blizzard when you Die": [
        "197,59"
    ],
    "{}% Chance to cast level {} Chilling Armor when you Die": [
        "197,60"
    ],
    "{}% Chance to cast level {} Fire Mastery when you Die": [
        "197,61"
    ],
    "{}% Chance to cast level {} Hydra when you Die": [
        "197,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery when you Die": [
        "197,63"
    ],
    "{}% Chance to cast level {} Frozen Orb when you Die": [
        "197,64"
    ],
    "{}% Chance to cast level {} Cold Mastery when you Die": [
        "197,65"
    ],
    "{}% Chance to cast level {} Amplify Damage when you Die": [
        "197,66"
    ],
    "{}% Chance to cast level {} Teeth when you Die": [
        "197,67"
    ],
    "{}% Chance to cast level {} Bone Armor when you Die": [
        "197,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery when you Die": [
        "197,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton when you Die": [
        "197,70"
    ],
    "{}% Chance to cast level {} Dim Vision when you Die": [
        "197,71"
    ],
    "{}% Chance to cast level {} Weaken when you Die": [
        "197,72"
    ],
    "{}% Chance to cast level {} Poison Dagger when you Die": [
        "197,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion when you Die": [
        "197,74"
    ],
    "{}% Chance to cast level {} Clay Golem when you Die": [
        "197,75"
    ],
    "{}% Chance to cast level {} Iron Maiden when you Die": [
        "197,76"
    ],
    "{}% Chance to cast level {} Terror when you Die": [
        "197,77"
    ],
    "{}% Chance to cast level {} Bone Wall when you Die": [
        "197,78"
    ],
    "{}% Chance to cast level {} Golem Mastery when you Die": [
        "197,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage when you Die": [
        "197,80"
    ],
    "{}% Chance to cast level {} Confuse when you Die": [
        "197,81"
    ],
    "{}% Chance to cast level {} Life Tap when you Die": [
        "197,82"
    ],
    "{}% Chance to cast level {} Poison Explosion when you Die": [
        "197,83"
    ],
    "{}% Chance to cast level {} Bone Spear when you Die": [
        "197,84"
    ],
    "{}% Chance to cast level {} Blood Golem when you Die": [
        "197,85"
    ],
    "{}% Chance to cast level {} Attract when you Die": [
        "197,86"
    ],
    "{}% Chance to cast level {} Decrepify when you Die": [
        "197,87"
    ],
    "{}% Chance to cast level {} Bone Prison when you Die": [
        "197,88"
    ],
    "{}% Chance to cast level {} Summon Resist when you Die": [
        "197,89"
    ],
    "{}% Chance to cast level {} Iron Golem when you Die": [
        "197,90"
    ],
    "{}% Chance to cast level {} Lower Resist when you Die": [
        "197,91"
    ],
    "{}% Chance to cast level {} Poison Nova when you Die": [
        "197,92"
    ],
    "{}% Chance to cast level {} Bone Spirit when you Die": [
        "197,93"
    ],
    "{}% Chance to cast level {} Fire Golem when you Die": [
        "197,94"
    ],
    "{}% Chance to cast level {} Revive when you Die": [
        "197,95"
    ],
    "{}% Chance to cast level {} Sacrifice when you Die": [
        "197,96"
    ],
    "{}% Chance to cast level {} Smite when you Die": [
        "197,97"
    ],
    "{}% Chance to cast level {} Might when you Die": [
        "197,98"
    ],
    "{}% Chance to cast level {} Prayer when you Die": [
        "197,99"
    ],
    "{}% Chance to cast level {} Resist Fire when you Die": [
        "197,100"
    ],
    "{}% Chance to cast level {} Holy Bolt when you Die": [
        "197,101"
    ],
    "{}% Chance to cast level {} Holy Fire when you Die": [
        "197,102"
    ],
    "{}% Chance to cast level {} Thorns when you Die": [
        "197,103"
    ],
    "{}% Chance to cast level {} Defiance when you Die": [
        "197,104"
    ],
    "{}% Chance to cast level {} Resist Cold when you Die": [
        "197,105"
    ],
    "{}% Chance to cast level {} Zeal when you Die": [
        "197,106"
    ],
    "{}% Chance to cast level {} Charge when you Die": [
        "197,107"
    ],
    "{}% Chance to cast level {} Blessed Aim when you Die": [
        "197,108"
    ],
    "{}% Chance to cast level {} Cleansing when you Die": [
        "197,109"
    ],
    "{}% Chance to cast level {} Resist Lightning when you Die": [
        "197,110"
    ],
    "{}% Chance to cast level {} Vengeance when you Die": [
        "197,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer when you Die": [
        "197,112"
    ],
    "{}% Chance to cast level {} Concentration when you Die": [
        "197,113"
    ],
    "{}% Chance to cast level {} Holy Freeze when you Die": [
        "197,114"
    ],
    "{}% Chance to cast level {} Vigor when you Die": [
        "197,115"
    ],
    "{}% Chance to cast level {} Conversion when you Die": [
        "197,116"
    ],
    "{}% Chance to cast level {} Holy Shield when you Die": [
        "197,117"
    ],
    "{}% Chance to cast level {} Holy Shock when you Die": [
        "197,118"
    ],
    "{}% Chance to cast level {} Sanctuary when you Die": [
        "197,119"
    ],
    "{}% Chance to cast level {} Meditation when you Die": [
        "197,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens when you Die": [
        "197,121"
    ],
    "{}% Chance to cast level {} Fanaticism when you Die": [
        "197,122"
    ],
    "{}% Chance to cast level {} Conviction when you Die": [
        "197,123"
    ],
    "{}% Chance to cast level {} Redemption when you Die": [
        "197,124"
    ],
    "{}% Chance to cast level {} Salvation when you Die": [
        "197,125"
    ],
    "{}% Chance to cast level {} Bash when you Die": [
        "197,126"
    ],
    "{}% Chance to cast level {} Blade Mastery when you Die": [
        "197,127"
    ],
    "{}% Chance to cast level {} Axe Mastery when you Die": [
        "197,128"
    ],
    "{}% Chance to cast level {} Mace Mastery when you Die": [
        "197,129"
    ],
    "{}% Chance to cast level {} Howl when you Die": [
        "197,130"
    ],
    "{}% Chance to cast level {} Find Potion when you Die": [
        "197,131"
    ],
    "{}% Chance to cast level {} Leap when you Die": [
        "197,132"
    ],
    "{}% Chance to cast level {} Double Swing when you Die": [
        "197,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery when you Die": [
        "197,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery when you Die": [
        "197,135"
    ],
    "{}% Chance to cast level {} Spear Mastery when you Die": [
        "197,136"
    ],
    "{}% Chance to cast level {} Taunt when you Die": [
        "197,137"
    ],
    "{}% Chance to cast level {} Shout when you Die": [
        "197,138"
    ],
    "{}% Chance to cast level {} Stun when you Die": [
        "197,139"
    ],
    "{}% Chance to cast level {} Double Throw when you Die": [
        "197,140"
    ],
    "{}% Chance to cast level {} Increased Stamina when you Die": [
        "197,141"
    ],
    "{}% Chance to cast level {} Find Item when you Die": [
        "197,142"
    ],
    "{}% Chance to cast level {} Leap Attack when you Die": [
        "197,143"
    ],
    "{}% Chance to cast level {} Concentrate when you Die": [
        "197,144"
    ],
    "{}% Chance to cast level {} Iron Skin when you Die": [
        "197,145"
    ],
    "{}% Chance to cast level {} Battle Cry when you Die": [
        "197,146"
    ],
    "{}% Chance to cast level {} Frenzy when you Die": [
        "197,147"
    ],
    "{}% Chance to cast level {} Increased Speed when you Die": [
        "197,148"
    ],
    "{}% Chance to cast level {} Battle Orders when you Die": [
        "197,149"
    ],
    "{}% Chance to cast level {} Grim Ward when you Die": [
        "197,150"
    ],
    "{}% Chance to cast level {} Whirlwind when you Die": [
        "197,151"
    ],
    "{}% Chance to cast level {} Berserk when you Die": [
        "197,152"
    ],
    "{}% Chance to cast level {} Natural Resistance when you Die": [
        "197,153"
    ],
    "{}% Chance to cast level {} War Cry when you Die": [
        "197,154"
    ],
    "{}% Chance to cast level {} Battle Command when you Die": [
        "197,155"
    ],
    "{}% Chance to cast level {} Raven when you Die": [
        "197,221"
    ],
    "{}% Chance to cast level {} Poison Creeper when you Die": [
        "197,222"
    ],
    "{}% Chance to cast level {} Werewolf when you Die": [
        "197,223"
    ],
    "{}% Chance to cast level {} Lycanthropy when you Die": [
        "197,224"
    ],
    "{}% Chance to cast level {} Firestorm when you Die": [
        "197,225"
    ],
    "{}% Chance to cast level {} Oak Sage when you Die": [
        "197,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf when you Die": [
        "197,227"
    ],
    "{}% Chance to cast level {} Werebear when you Die": [
        "197,228"
    ],
    "{}% Chance to cast level {} Molten Boulder when you Die": [
        "197,229"
    ],
    "{}% Chance to cast level {} Arctic Blast when you Die": [
        "197,230"
    ],
    "{}% Chance to cast level {} Carrion Vine when you Die": [
        "197,231"
    ],
    "{}% Chance to cast level {} Feral Rage when you Die": [
        "197,232"
    ],
    "{}% Chance to cast level {} Maul when you Die": [
        "197,233"
    ],
    "{}% Chance to cast level {} Fissure when you Die": [
        "197,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor when you Die": [
        "197,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine when you Die": [
        "197,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf when you Die": [
        "197,237"
    ],
    "{}% Chance to cast level {} Rabies when you Die": [
        "197,238"
    ],
    "{}% Chance to cast level {} Fire Claws when you Die": [
        "197,239"
    ],
    "{}% Chance to cast level {} Twister when you Die": [
        "197,240"
    ],
    "{}% Chance to cast level {} Solar Creeper when you Die": [
        "197,241"
    ],
    "{}% Chance to cast level {} Hunger when you Die": [
        "197,242"
    ],
    "{}% Chance to cast level {} Shock Wave when you Die": [
        "197,243"
    ],
    "{}% Chance to cast level {} Volcano when you Die": [
        "197,244"
    ],
    "{}% Chance to cast level {} Tornado when you Die": [
        "197,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs when you Die": [
        "197,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly when you Die": [
        "197,247"
    ],
    "{}% Chance to cast level {} Fury when you Die": [
        "197,248"
    ],
    "{}% Chance to cast level {} Armageddon when you Die": [
        "197,249"
    ],
    "{}% Chance to cast level {} Hurricane when you Die": [
        "197,250"
    ],
    "{}% Chance to cast level {} Fire Blast when you Die": [
        "197,251"
    ],
    "{}% Chance to cast level {} Claw Mastery when you Die": [
        "197,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer when you Die": [
        "197,253"
    ],
    "{}% Chance to cast level {} Tiger Strike when you Die": [
        "197,254"
    ],
    "{}% Chance to cast level {} Dragon Talon when you Die": [
        "197,255"
    ],
    "{}% Chance to cast level {} Shock Web when you Die": [
        "197,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel when you Die": [
        "197,257"
    ],
    "{}% Chance to cast level {} Burst of Speed when you Die": [
        "197,258"
    ],
    "{}% Chance to cast level {} Fists of Fire when you Die": [
        "197,259"
    ],
    "{}% Chance to cast level {} Dragon Claw when you Die": [
        "197,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry when you Die": [
        "197,261"
    ],
    "{}% Chance to cast level {} Wake of Fire when you Die": [
        "197,262"
    ],
    "{}% Chance to cast level {} Weapon Block when you Die": [
        "197,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows when you Die": [
        "197,264"
    ],
    "{}% Chance to cast level {} Cobra Strike when you Die": [
        "197,265"
    ],
    "{}% Chance to cast level {} Blade Fury when you Die": [
        "197,266"
    ],
    "{}% Chance to cast level {} Fade when you Die": [
        "197,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior when you Die": [
        "197,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder when you Die": [
        "197,269"
    ],
    "{}% Chance to cast level {} Dragon Tail when you Die": [
        "197,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry when you Die": [
        "197,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno when you Die": [
        "197,272"
    ],
    "{}% Chance to cast level {} Mind Blast when you Die": [
        "197,273"
    ],
    "{}% Chance to cast level {} Blades of Ice when you Die": [
        "197,274"
    ],
    "{}% Chance to cast level {} Dragon Flight when you Die": [
        "197,275"
    ],
    "{}% Chance to cast level {} Death Sentry when you Die": [
        "197,276"
    ],
    "{}% Chance to cast level {} Blade Shield when you Die": [
        "197,277"
    ],
    "{}% Chance to cast level {} Venom when you Die": [
        "197,278"
    ],
    "{}% Chance to cast level {} Shadow Master when you Die": [
        "197,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike when you Die": [
        "197,280"
    ],
    "{}% Chance to cast level {} Magic Arrow when you Level-Up": [
        "199,6"
    ],
    "{}% Chance to cast level {} Fire Arrow when you Level-Up": [
        "199,7"
    ],
    "{}% Chance to cast level {} Inner Sight when you Level-Up": [
        "199,8"
    ],
    "{}% Chance to cast level {} Critical Strike when you Level-Up": [
        "199,9"
    ],
    "{}% Chance to cast level {} Jab when you Level-Up": [
        "199,10"
    ],
    "{}% Chance to cast level {} Cold Arrow when you Level-Up": [
        "199,11"
    ],
    "{}% Chance to cast level {} Multiple Shot when you Level-Up": [
        "199,12"
    ],
    "{}% Chance to cast level {} Dodge when you Level-Up": [
        "199,13"
    ],
    "{}% Chance to cast level {} Power Strike when you Level-Up": [
        "199,14"
    ],
    "{}% Chance to cast level {} Poison Javelin when you Level-Up": [
        "199,15"
    ],
    "{}% Chance to cast level {} Exploding Arrow when you Level-Up": [
        "199,16"
    ],
    "{}% Chance to cast level {} Slow Missiles when you Level-Up": [
        "199,17"
    ],
    "{}% Chance to cast level {} Avoid when you Level-Up": [
        "199,18"
    ],
    "{}% Chance to cast level {} Impale when you Level-Up": [
        "199,19"
    ],
    "{}% Chance to cast level {} Lightning Bolt when you Level-Up": [
        "199,20"
    ],
    "{}% Chance to cast level {} Ice Arrow when you Level-Up": [
        "199,21"
    ],
    "{}% Chance to cast level {} Guided Arrow when you Level-Up": [
        "199,22"
    ],
    "{}% Chance to cast level {} Penetrate when you Level-Up": [
        "199,23"
    ],
    "{}% Chance to cast level {} Charged Strike when you Level-Up": [
        "199,24"
    ],
    "{}% Chance to cast level {} Plague Javelin when you Level-Up": [
        "199,25"
    ],
    "{}% Chance to cast level {} Strafe when you Level-Up": [
        "199,26"
    ],
    "{}% Chance to cast level {} Immolation Arrow when you Level-Up": [
        "199,27"
    ],
    "{}% Chance to cast level {} Decoy when you Level-Up": [
        "199,28"
    ],
    "{}% Chance to cast level {} Evade when you Level-Up": [
        "199,29"
    ],
    "{}% Chance to cast level {} Fend when you Level-Up": [
        "199,30"
    ],
    "{}% Chance to cast level {} Freezing Arrow when you Level-Up": [
        "199,31"
    ],
    "{}% Chance to cast level {} Valkyrie when you Level-Up": [
        "199,32"
    ],
    "{}% Chance to cast level {} Pierce when you Level-Up": [
        "199,33"
    ],
    "{}% Chance to cast level {} Lightning Strike when you Level-Up": [
        "199,34"
    ],
    "{}% Chance to cast level {} Lightning Fury when you Level-Up": [
        "199,35"
    ],
    "{}% Chance to cast level {} Fire Bolt when you Level-Up": [
        "199,36"
    ],
    "{}% Chance to cast level {} Warmth when you Level-Up": [
        "199,37"
    ],
    "{}% Chance to cast level {} Charged Bolt when you Level-Up": [
        "199,38"
    ],
    "{}% Chance to cast level {} Ice Bolt when you Level-Up": [
        "199,39"
    ],
    "{}% Chance to cast level {} Frozen Armor when you Level-Up": [
        "199,40"
    ],
    "{}% Chance to cast level {} Inferno when you Level-Up": [
        "199,41"
    ],
    "{}% Chance to cast level {} Static Field when you Level-Up": [
        "199,42"
    ],
    "{}% Chance to cast level {} Telekinesis when you Level-Up": [
        "199,43"
    ],
    "{}% Chance to cast level {} Frost Nova when you Level-Up": [
        "199,44"
    ],
    "{}% Chance to cast level {} Ice Blast when you Level-Up": [
        "199,45"
    ],
    "{}% Chance to cast level {} Blaze when you Level-Up": [
        "199,46"
    ],
    "{}% Chance to cast level {} Fire Ball when you Level-Up": [
        "199,47"
    ],
    "{}% Chance to cast level {} Nova when you Level-Up": [
        "199,48"
    ],
    "{}% Chance to cast level {} Lightning when you Level-Up": [
        "199,49"
    ],
    "{}% Chance to cast level {} Shiver Armor when you Level-Up": [
        "199,50"
    ],
    "{}% Chance to cast level {} Fire Wall when you Level-Up": [
        "199,51"
    ],
    "{}% Chance to cast level {} Enchant when you Level-Up": [
        "199,52"
    ],
    "{}% Chance to cast level {} Chain Lightning when you Level-Up": [
        "199,53"
    ],
    "{}% Chance to cast level {} Teleport when you Level-Up": [
        "199,54"
    ],
    "{}% Chance to cast level {} Glacial Spike when you Level-Up": [
        "199,55"
    ],
    "{}% Chance to cast level {} Meteor when you Level-Up": [
        "199,56"
    ],
    "{}% Chance to cast level {} Thunder Storm when you Level-Up": [
        "199,57"
    ],
    "{}% Chance to cast level {} Energy Shield when you Level-Up": [
        "199,58"
    ],
    "{}% Chance to cast level {} Blizzard when you Level-Up": [
        "199,59"
    ],
    "{}% Chance to cast level {} Chilling Armor when you Level-Up": [
        "199,60"
    ],
    "{}% Chance to cast level {} Fire Mastery when you Level-Up": [
        "199,61"
    ],
    "{}% Chance to cast level {} Hydra when you Level-Up": [
        "199,62"
    ],
    "{}% Chance to cast level {} Lightning Mastery when you Level-Up": [
        "199,63"
    ],
    "{}% Chance to cast level {} Frozen Orb when you Level-Up": [
        "199,64"
    ],
    "{}% Chance to cast level {} Cold Mastery when you Level-Up": [
        "199,65"
    ],
    "{}% Chance to cast level {} Amplify Damage when you Level-Up": [
        "199,66"
    ],
    "{}% Chance to cast level {} Teeth when you Level-Up": [
        "199,67"
    ],
    "{}% Chance to cast level {} Bone Armor when you Level-Up": [
        "199,68"
    ],
    "{}% Chance to cast level {} Skeleton Mastery when you Level-Up": [
        "199,69"
    ],
    "{}% Chance to cast level {} Raise Skeleton when you Level-Up": [
        "199,70"
    ],
    "{}% Chance to cast level {} Dim Vision when you Level-Up": [
        "199,71"
    ],
    "{}% Chance to cast level {} Weaken when you Level-Up": [
        "199,72"
    ],
    "{}% Chance to cast level {} Poison Dagger when you Level-Up": [
        "199,73"
    ],
    "{}% Chance to cast level {} Corpse Explosion when you Level-Up": [
        "199,74"
    ],
    "{}% Chance to cast level {} Clay Golem when you Level-Up": [
        "199,75"
    ],
    "{}% Chance to cast level {} Iron Maiden when you Level-Up": [
        "199,76"
    ],
    "{}% Chance to cast level {} Terror when you Level-Up": [
        "199,77"
    ],
    "{}% Chance to cast level {} Bone Wall when you Level-Up": [
        "199,78"
    ],
    "{}% Chance to cast level {} Golem Mastery when you Level-Up": [
        "199,79"
    ],
    "{}% Chance to cast level {} Raise Skeletal Mage when you Level-Up": [
        "199,80"
    ],
    "{}% Chance to cast level {} Confuse when you Level-Up": [
        "199,81"
    ],
    "{}% Chance to cast level {} Life Tap when you Level-Up": [
        "199,82"
    ],
    "{}% Chance to cast level {} Poison Explosion when you Level-Up": [
        "199,83"
    ],
    "{}% Chance to cast level {} Bone Spear when you Level-Up": [
        "199,84"
    ],
    "{}% Chance to cast level {} Blood Golem when you Level-Up": [
        "199,85"
    ],
    "{}% Chance to cast level {} Attract when you Level-Up": [
        "199,86"
    ],
    "{}% Chance to cast level {} Decrepify when you Level-Up": [
        "199,87"
    ],
    "{}% Chance to cast level {} Bone Prison when you Level-Up": [
        "199,88"
    ],
    "{}% Chance to cast level {} Summon Resist when you Level-Up": [
        "199,89"
    ],
    "{}% Chance to cast level {} Iron Golem when you Level-Up": [
        "199,90"
    ],
    "{}% Chance to cast level {} Lower Resist when you Level-Up": [
        "199,91"
    ],
    "{}% Chance to cast level {} Poison Nova when you Level-Up": [
        "199,92"
    ],
    "{}% Chance to cast level {} Bone Spirit when you Level-Up": [
        "199,93"
    ],
    "{}% Chance to cast level {} Fire Golem when you Level-Up": [
        "199,94"
    ],
    "{}% Chance to cast level {} Revive when you Level-Up": [
        "199,95"
    ],
    "{}% Chance to cast level {} Sacrifice when you Level-Up": [
        "199,96"
    ],
    "{}% Chance to cast level {} Smite when you Level-Up": [
        "199,97"
    ],
    "{}% Chance to cast level {} Might when you Level-Up": [
        "199,98"
    ],
    "{}% Chance to cast level {} Prayer when you Level-Up": [
        "199,99"
    ],
    "{}% Chance to cast level {} Resist Fire when you Level-Up": [
        "199,100"
    ],
    "{}% Chance to cast level {} Holy Bolt when you Level-Up": [
        "199,101"
    ],
    "{}% Chance to cast level {} Holy Fire when you Level-Up": [
        "199,102"
    ],
    "{}% Chance to cast level {} Thorns when you Level-Up": [
        "199,103"
    ],
    "{}% Chance to cast level {} Defiance when you Level-Up": [
        "199,104"
    ],
    "{}% Chance to cast level {} Resist Cold when you Level-Up": [
        "199,105"
    ],
    "{}% Chance to cast level {} Zeal when you Level-Up": [
        "199,106"
    ],
    "{}% Chance to cast level {} Charge when you Level-Up": [
        "199,107"
    ],
    "{}% Chance to cast level {} Blessed Aim when you Level-Up": [
        "199,108"
    ],
    "{}% Chance to cast level {} Cleansing when you Level-Up": [
        "199,109"
    ],
    "{}% Chance to cast level {} Resist Lightning when you Level-Up": [
        "199,110"
    ],
    "{}% Chance to cast level {} Vengeance when you Level-Up": [
        "199,111"
    ],
    "{}% Chance to cast level {} Blessed Hammer when you Level-Up": [
        "199,112"
    ],
    "{}% Chance to cast level {} Concentration when you Level-Up": [
        "199,113"
    ],
    "{}% Chance to cast level {} Holy Freeze when you Level-Up": [
        "199,114"
    ],
    "{}% Chance to cast level {} Vigor when you Level-Up": [
        "199,115"
    ],
    "{}% Chance to cast level {} Conversion when you Level-Up": [
        "199,116"
    ],
    "{}% Chance to cast level {} Holy Shield when you Level-Up": [
        "199,117"
    ],
    "{}% Chance to cast level {} Holy Shock when you Level-Up": [
        "199,118"
    ],
    "{}% Chance to cast level {} Sanctuary when you Level-Up": [
        "199,119"
    ],
    "{}% Chance to cast level {} Meditation when you Level-Up": [
        "199,120"
    ],
    "{}% Chance to cast level {} Fist of the Heavens when you Level-Up": [
        "199,121"
    ],
    "{}% Chance to cast level {} Fanaticism when you Level-Up": [
        "199,122"
    ],
    "{}% Chance to cast level {} Conviction when you Level-Up": [
        "199,123"
    ],
    "{}% Chance to cast level {} Redemption when you Level-Up": [
        "199,124"
    ],
    "{}% Chance to cast level {} Salvation when you Level-Up": [
        "199,125"
    ],
    "{}% Chance to cast level {} Bash when you Level-Up": [
        "199,126"
    ],
    "{}% Chance to cast level {} Blade Mastery when you Level-Up": [
        "199,127"
    ],
    "{}% Chance to cast level {} Axe Mastery when you Level-Up": [
        "199,128"
    ],
    "{}% Chance to cast level {} Mace Mastery when you Level-Up": [
        "199,129"
    ],
    "{}% Chance to cast level {} Howl when you Level-Up": [
        "199,130"
    ],
    "{}% Chance to cast level {} Find Potion when you Level-Up": [
        "199,131"
    ],
    "{}% Chance to cast level {} Leap when you Level-Up": [
        "199,132"
    ],
    "{}% Chance to cast level {} Double Swing when you Level-Up": [
        "199,133"
    ],
    "{}% Chance to cast level {} Polearm Mastery when you Level-Up": [
        "199,134"
    ],
    "{}% Chance to cast level {} Throwing Mastery when you Level-Up": [
        "199,135"
    ],
    "{}% Chance to cast level {} Spear Mastery when you Level-Up": [
        "199,136"
    ],
    "{}% Chance to cast level {} Taunt when you Level-Up": [
        "199,137"
    ],
    "{}% Chance to cast level {} Shout when you Level-Up": [
        "199,138"
    ],
    "{}% Chance to cast level {} Stun when you Level-Up": [
        "199,139"
    ],
    "{}% Chance to cast level {} Double Throw when you Level-Up": [
        "199,140"
    ],
    "{}% Chance to cast level {} Increased Stamina when you Level-Up": [
        "199,141"
    ],
    "{}% Chance to cast level {} Find Item when you Level-Up": [
        "199,142"
    ],
    "{}% Chance to cast level {} Leap Attack when you Level-Up": [
        "199,143"
    ],
    "{}% Chance to cast level {} Concentrate when you Level-Up": [
        "199,144"
    ],
    "{}% Chance to cast level {} Iron Skin when you Level-Up": [
        "199,145"
    ],
    "{}% Chance to cast level {} Battle Cry when you Level-Up": [
        "199,146"
    ],
    "{}% Chance to cast level {} Frenzy when you Level-Up": [
        "199,147"
    ],
    "{}% Chance to cast level {} Increased Speed when you Level-Up": [
        "199,148"
    ],
    "{}% Chance to cast level {} Battle Orders when you Level-Up": [
        "199,149"
    ],
    "{}% Chance to cast level {} Grim Ward when you Level-Up": [
        "199,150"
    ],
    "{}% Chance to cast level {} Whirlwind when you Level-Up": [
        "199,151"
    ],
    "{}% Chance to cast level {} Berserk when you Level-Up": [
        "199,152"
    ],
    "{}% Chance to cast level {} Natural Resistance when you Level-Up": [
        "199,153"
    ],
    "{}% Chance to cast level {} War Cry when you Level-Up": [
        "199,154"
    ],
    "{}% Chance to cast level {} Battle Command when you Level-Up": [
        "199,155"
    ],
    "{}% Chance to cast level {} Raven when you Level-Up": [
        "199,221"
    ],
    "{}% Chance to cast level {} Poison Creeper when you Level-Up": [
        "199,222"
    ],
    "{}% Chance to cast level {} Werewolf when you Level-Up": [
        "199,223"
    ],
    "{}% Chance to cast level {} Lycanthropy when you Level-Up": [
        "199,224"
    ],
    "{}% Chance to cast level {} Firestorm when you Level-Up": [
        "199,225"
    ],
    "{}% Chance to cast level {} Oak Sage when you Level-Up": [
        "199,226"
    ],
    "{}% Chance to cast level {} Summon Spirit Wolf when you Level-Up": [
        "199,227"
    ],
    "{}% Chance to cast level {} Werebear when you Level-Up": [
        "199,228"
    ],
    "{}% Chance to cast level {} Molten Boulder when you Level-Up": [
        "199,229"
    ],
    "{}% Chance to cast level {} Arctic Blast when you Level-Up": [
        "199,230"
    ],
    "{}% Chance to cast level {} Carrion Vine when you Level-Up": [
        "199,231"
    ],
    "{}% Chance to cast level {} Feral Rage when you Level-Up": [
        "199,232"
    ],
    "{}% Chance to cast level {} Maul when you Level-Up": [
        "199,233"
    ],
    "{}% Chance to cast level {} Fissure when you Level-Up": [
        "199,234"
    ],
    "{}% Chance to cast level {} Cyclone Armor when you Level-Up": [
        "199,235"
    ],
    "{}% Chance to cast level {} Heart of Wolverine when you Level-Up": [
        "199,236"
    ],
    "{}% Chance to cast level {} Summon Dire Wolf when you Level-Up": [
        "199,237"
    ],
    "{}% Chance to cast level {} Rabies when you Level-Up": [
        "199,238"
    ],
    "{}% Chance to cast level {} Fire Claws when you Level-Up": [
        "199,239"
    ],
    "{}% Chance to cast level {} Twister when you Level-Up": [
        "199,240"
    ],
    "{}% Chance to cast level {} Solar Creeper when you Level-Up": [
        "199,241"
    ],
    "{}% Chance to cast level {} Hunger when you Level-Up": [
        "199,242"
    ],
    "{}% Chance to cast level {} Shock Wave when you Level-Up": [
        "199,243"
    ],
    "{}% Chance to cast level {} Volcano when you Level-Up": [
        "199,244"
    ],
    "{}% Chance to cast level {} Tornado when you Level-Up": [
        "199,245"
    ],
    "{}% Chance to cast level {} Spirit of Barbs when you Level-Up": [
        "199,246"
    ],
    "{}% Chance to cast level {} Summon Grizzly when you Level-Up": [
        "199,247"
    ],
    "{}% Chance to cast level {} Fury when you Level-Up": [
        "199,248"
    ],
    "{}% Chance to cast level {} Armageddon when you Level-Up": [
        "199,249"
    ],
    "{}% Chance to cast level {} Hurricane when you Level-Up": [
        "199,250"
    ],
    "{}% Chance to cast level {} Fire Blast when you Level-Up": [
        "199,251"
    ],
    "{}% Chance to cast level {} Claw Mastery when you Level-Up": [
        "199,252"
    ],
    "{}% Chance to cast level {} Psychic Hammer when you Level-Up": [
        "199,253"
    ],
    "{}% Chance to cast level {} Tiger Strike when you Level-Up": [
        "199,254"
    ],
    "{}% Chance to cast level {} Dragon Talon when you Level-Up": [
        "199,255"
    ],
    "{}% Chance to cast level {} Shock Web when you Level-Up": [
        "199,256"
    ],
    "{}% Chance to cast level {} Blade Sentinel when you Level-Up": [
        "199,257"
    ],
    "{}% Chance to cast level {} Burst of Speed when you Level-Up": [
        "199,258"
    ],
    "{}% Chance to cast level {} Fists of Fire when you Level-Up": [
        "199,259"
    ],
    "{}% Chance to cast level {} Dragon Claw when you Level-Up": [
        "199,260"
    ],
    "{}% Chance to cast level {} Charged Bolt Sentry when you Level-Up": [
        "199,261"
    ],
    "{}% Chance to cast level {} Wake of Fire when you Level-Up": [
        "199,262"
    ],
    "{}% Chance to cast level {} Weapon Block when you Level-Up": [
        "199,263"
    ],
    "{}% Chance to cast level {} Cloak of Shadows when you Level-Up": [
        "199,264"
    ],
    "{}% Chance to cast level {} Cobra Strike when you Level-Up": [
        "199,265"
    ],
    "{}% Chance to cast level {} Blade Fury when you Level-Up": [
        "199,266"
    ],
    "{}% Chance to cast level {} Fade when you Level-Up": [
        "199,267"
    ],
    "{}% Chance to cast level {} Shadow Warrior when you Level-Up": [
        "199,268"
    ],
    "{}% Chance to cast level {} Claws of Thunder when you Level-Up": [
        "199,269"
    ],
    "{}% Chance to cast level {} Dragon Tail when you Level-Up": [
        "199,270"
    ],
    "{}% Chance to cast level {} Lightning Sentry when you Level-Up": [
        "199,271"
    ],
    "{}% Chance to cast level {} Wake of Inferno when you Level-Up": [
        "199,272"
    ],
    "{}% Chance to cast level {} Mind Blast when you Level-Up": [
        "199,273"
    ],
    "{}% Chance to cast level {} Blades of Ice when you Level-Up": [
        "199,274"
    ],
    "{}% Chance to cast level {} Dragon Flight when you Level-Up": [
        "199,275"
    ],
    "{}% Chance to cast level {} Death Sentry when you Level-Up": [
        "199,276"
    ],
    "{}% Chance to cast level {} Blade Shield when you Level-Up": [
        "199,277"
    ],
    "{}% Chance to cast level {} Venom when you Level-Up": [
        "199,278"
    ],
    "{}% Chance to cast level {} Shadow Master when you Level-Up": [
        "199,279"
    ],
    "{}% Chance to cast level {} Phoenix Strike when you Level-Up": [
        "199,280"
    ],
    "Required Level: {}": [
        "92"
    ],
    "+{} to Magic Arrow": [
        "97,6"
    ],
    "+{} to Fire Arrow": [
        "97,7"
    ],
    "+{} to Inner Sight": [
        "97,8"
    ],
    "+{} to Critical Strike": [
        "97,9"
    ],
    "+{} to Jab": [
        "97,10"
    ],
    "+{} to Cold Arrow": [
        "97,11"
    ],
    "+{} to Multiple Shot": [
        "97,12"
    ],
    "+{} to Dodge": [
        "97,13"
    ],
    "+{} to Power Strike": [
        "97,14"
    ],
    "+{} to Poison Javelin": [
        "97,15"
    ],
    "+{} to Exploding Arrow": [
        "97,16"
    ],
    "+{} to Slow Missiles": [
        "97,17"
    ],
    "+{} to Avoid": [
        "97,18"
    ],
    "+{} to Impale": [
        "97,19"
    ],
    "+{} to Lightning Bolt": [
        "97,20"
    ],
    "+{} to Ice Arrow": [
        "97,21"
    ],
    "+{} to Guided Arrow": [
        "97,22"
    ],
    "+{} to Penetrate": [
        "97,23"
    ],
    "+{} to Charged Strike": [
        "97,24"
    ],
    "+{} to Plague Javelin": [
        "97,25"
    ],
    "+{} to Strafe": [
        "97,26"
    ],
    "+{} to Immolation Arrow": [
        "97,27"
    ],
    "+{} to Decoy": [
        "97,28"
    ],
    "+{} to Evade": [
        "97,29"
    ],
    "+{} to Fend": [
        "97,30"
    ],
    "+{} to Freezing Arrow": [
        "97,31"
    ],
    "+{} to Valkyrie": [
        "97,32"
    ],
    "+{} to Pierce": [
        "97,33"
    ],
    "+{} to Lightning Strike": [
        "97,34"
    ],
    "+{} to Lightning Fury": [
        "97,35"
    ],
    "+{} to Fire Bolt": [
        "97,36"
    ],
    "+{} to Warmth": [
        "97,37"
    ],
    "+{} to Charged Bolt": [
        "97,38"
    ],
    "+{} to Ice Bolt": [
        "97,39"
    ],
    "+{} to Frozen Armor": [
        "97,40"
    ],
    "+{} to Inferno": [
        "97,41"
    ],
    "+{} to Static Field": [
        "97,42"
    ],
    "+{} to Telekinesis": [
        "97,43"
    ],
    "+{} to Frost Nova": [
        "97,44"
    ],
    "+{} to Ice Blast": [
        "97,45"
    ],
    "+{} to Blaze": [
        "97,46"
    ],
    "+{} to Fire Ball": [
        "97,47"
    ],
    "+{} to Nova": [
        "97,48"
    ],
    "+{} to Lightning": [
        "97,49"
    ],
    "+{} to Shiver Armor": [
        "97,50"
    ],
    "+{} to Fire Wall": [
        "97,51"
    ],
    "+{} to Enchant": [
        "97,52"
    ],
    "+{} to Chain Lightning": [
        "97,53"
    ],
    "+{} to Teleport": [
        "97,54"
    ],
    "+{} to Glacial Spike": [
        "97,55"
    ],
    "+{} to Meteor": [
        "97,56"
    ],
    "+{} to Thunder Storm": [
        "97,57"
    ],
    "+{} to Energy Shield": [
        "97,58"
    ],
    "+{} to Blizzard": [
        "97,59"
    ],
    "+{} to Chilling Armor": [
        "97,60"
    ],
    "+{} to Fire Mastery": [
        "97,61"
    ],
    "+{} to Hydra": [
        "97,62"
    ],
    "+{} to Lightning Mastery": [
        "97,63"
    ],
    "+{} to Frozen Orb": [
        "97,64"
    ],
    "+{} to Cold Mastery": [
        "97,65"
    ],
    "+{} to Amplify Damage": [
        "97,66"
    ],
    "+{} to Teeth": [
        "97,67"
    ],
    "+{} to Bone Armor": [
        "97,68"
    ],
    "+{} to Skeleton Mastery": [
        "97,69"
    ],
    "+{} to Raise Skeleton": [
        "97,70"
    ],
    "+{} to Dim Vision": [
        "97,71"
    ],
    "+{} to Weaken": [
        "97,72"
    ],
    "+{} to Poison Dagger": [
        "97,73"
    ],
    "+{} to Corpse Explosion": [
        "97,74"
    ],
    "+{} to Clay Golem": [
        "97,75"
    ],
    "+{} to Iron Maiden": [
        "97,76"
    ],
    "+{} to Terror": [
        "97,77"
    ],
    "+{} to Bone Wall": [
        "97,78"
    ],
    "+{} to Golem Mastery": [
        "97,79"
    ],
    "+{} to Raise Skeletal Mage": [
        "97,80"
    ],
    "+{} to Confuse": [
        "97,81"
    ],
    "+{} to Life Tap": [
        "97,82"
    ],
    "+{} to Poison Explosion": [
        "97,83"
    ],
    "+{} to Bone Spear": [
        "97,84"
    ],
    "+{} to Blood Golem": [
        "97,85"
    ],
    "+{} to Attract": [
        "97,86"
    ],
    "+{} to Decrepify": [
        "97,87"
    ],
    "+{} to Bone Prison": [
        "97,88"
    ],
    "+{} to Summon Resist": [
        "97,89"
    ],
    "+{} to Iron Golem": [
        "97,90"
    ],
    "+{} to Lower Resist": [
        "97,91"
    ],
    "+{} to Poison Nova": [
        "97,92"
    ],
    "+{} to Bone Spirit": [
        "97,93"
    ],
    "+{} to Fire Golem": [
        "97,94"
    ],
    "+{} to Revive": [
        "97,95"
    ],
    "+{} to Sacrifice": [
        "97,96"
    ],
    "+{} to Smite": [
        "97,97"
    ],
    "+{} to Might": [
        "97,98"
    ],
    "+{} to Prayer": [
        "97,99"
    ],
    "+{} to Resist Fire": [
        "97,100"
    ],
    "+{} to Holy Bolt": [
        "97,101"
    ],
    "+{} to Holy Fire": [
        "97,102"
    ],
    "+{} to Thorns": [
        "97,103"
    ],
    "+{} to Defiance": [
        "97,104"
    ],
    "+{} to Resist Cold": [
        "97,105"
    ],
    "+{} to Zeal": [
        "97,106"
    ],
    "+{} to Charge": [
        "97,107"
    ],
    "+{} to Blessed Aim": [
        "97,108"
    ],
    "+{} to Cleansing": [
        "97,109"
    ],
    "+{} to Resist Lightning": [
        "97,110"
    ],
    "+{} to Vengeance": [
        "97,111"
    ],
    "+{} to Blessed Hammer": [
        "97,112"
    ],
    "+{} to Concentration": [
        "97,113"
    ],
    "+{} to Holy Freeze": [
        "97,114"
    ],
    "+{} to Vigor": [
        "97,115"
    ],
    "+{} to Conversion": [
        "97,116"
    ],
    "+{} to Holy Shield": [
        "97,117"
    ],
    "+{} to Holy Shock": [
        "97,118"
    ],
    "+{} to Sanctuary": [
        "97,119"
    ],
    "+{} to Meditation": [
        "97,120"
    ],
    "+{} to Fist of the Heavens": [
        "97,121"
    ],
    "+{} to Fanaticism": [
        "97,122"
    ],
    "+{} to Conviction": [
        "97,123"
    ],
    "+{} to Redemption": [
        "97,124"
    ],
    "+{} to Salvation": [
        "97,125"
    ],
    "+{} to Bash": [
        "97,126"
    ],
    "+{} to Blade Mastery": [
        "97,127"
    ],
    "+{} to Axe Mastery": [
        "97,128"
    ],
    "+{} to Mace Mastery": [
        "97,129"
    ],
    "+{} to Howl": [
        "97,130"
    ],
    "+{} to Find Potion": [
        "97,131"
    ],
    "+{} to Leap": [
        "97,132"
    ],
    "+{} to Double Swing": [
        "97,133"
    ],
    "+{} to Polearm Mastery": [
        "97,134"
    ],
    "+{} to Throwing Mastery": [
        "97,135"
    ],
    "+{} to Spear Mastery": [
        "97,136"
    ],
    "+{} to Taunt": [
        "97,137"
    ],
    "+{} to Shout": [
        "97,138"
    ],
    "+{} to Stun": [
        "97,139"
    ],
    "+{} to Double Throw": [
        "97,140"
    ],
    "+{} to Increased Stamina": [
        "97,141"
    ],
    "+{} to Find Item": [
        "97,142"
    ],
    "+{} to Leap Attack": [
        "97,143"
    ],
    "+{} to Concentrate": [
        "97,144"
    ],
    "+{} to Iron Skin": [
        "97,145"
    ],
    "+{} to Battle Cry": [
        "97,146"
    ],
    "+{} to Frenzy": [
        "97,147"
    ],
    "+{} to Increased Speed": [
        "97,148"
    ],
    "+{} to Battle Orders": [
        "97,149"
    ],
    "+{} to Grim Ward": [
        "97,150"
    ],
    "+{} to Whirlwind": [
        "97,151"
    ],
    "+{} to Berserk": [
        "97,152"
    ],
    "+{} to Natural Resistance": [
        "97,153"
    ],
    "+{} to War Cry": [
        "97,154"
    ],
    "+{} to Battle Command": [
        "97,155"
    ],
    "+{} to Raven": [
        "97,221"
    ],
    "+{} to Poison Creeper": [
        "97,222"
    ],
    "+{} to Werewolf": [
        "97,223"
    ],
    "+{} to Lycanthropy": [
        "97,224"
    ],
    "+{} to Firestorm": [
        "97,225"
    ],
    "+{} to Oak Sage": [
        "97,226"
    ],
    "+{} to Summon Spirit Wolf": [
        "97,227"
    ],
    "+{} to Werebear": [
        "97,228"
    ],
    "+{} to Molten Boulder": [
        "97,229"
    ],
    "+{} to Arctic Blast": [
        "97,230"
    ],
    "+{} to Carrion Vine": [
        "97,231"
    ],
    "+{} to Feral Rage": [
        "97,232"
    ],
    "+{} to Maul": [
        "97,233"
    ],
    "+{} to Fissure": [
        "97,234"
    ],
    "+{} to Cyclone Armor": [
        "97,235"
    ],
    "+{} to Heart of Wolverine": [
        "97,236"
    ],
    "+{} to Summon Dire Wolf": [
        "97,237"
    ],
    "+{} to Rabies": [
        "97,238"
    ],
    "+{} to Fire Claws": [
        "97,239"
    ],
    "+{} to Twister": [
        "97,240"
    ],
    "+{} to Solar Creeper": [
        "97,241"
    ],
    "+{} to Hunger": [
        "97,242"
    ],
    "+{} to Shock Wave": [
        "97,243"
    ],
    "+{} to Volcano": [
        "97,244"
    ],
    "+{} to Tornado": [
        "97,245"
    ],
    "+{} to Spirit of Barbs": [
        "97,246"
    ],
    "+{} to Summon Grizzly": [
        "97,247"
    ],
    "+{} to Fury": [
        "97,248"
    ],
    "+{} to Armageddon": [
        "97,249"
    ],
    "+{} to Hurricane": [
        "97,250"
    ],
    "+{} to Fire Blast": [
        "97,251"
    ],
    "+{} to Claw Mastery": [
        "97,252"
    ],
    "+{} to Psychic Hammer": [
        "97,253"
    ],
    "+{} to Tiger Strike": [
        "97,254"
    ],
    "+{} to Dragon Talon": [
        "97,255"
    ],
    "+{} to Shock Web": [
        "97,256"
    ],
    "+{} to Blade Sentinel": [
        "97,257"
    ],
    "+{} to Burst of Speed": [
        "97,258"
    ],
    "+{} to Fists of Fire": [
        "97,259"
    ],
    "+{} to Dragon Claw": [
        "97,260"
    ],
    "+{} to Charged Bolt Sentry": [
        "97,261"
    ],
    "+{} to Wake of Fire": [
        "97,262"
    ],
    "+{} to Weapon Block": [
        "97,263"
    ],
    "+{} to Cloak of Shadows": [
        "97,264"
    ],
    "+{} to Cobra Strike": [
        "97,265"
    ],
    "+{} to Blade Fury": [
        "97,266"
    ],
    "+{} to Fade": [
        "97,267"
    ],
    "+{} to Shadow Warrior": [
        "97,268"
    ],
    "+{} to Claws of Thunder": [
        "97,269"
    ],
    "+{} to Dragon Tail": [
        "97,270"
    ],
    "+{} to Lightning Sentry": [
        "97,271"
    ],
    "+{} to Wake of Inferno": [
        "97,272"
    ],
    "+{} to Mind Blast": [
        "97,273"
    ],
    "+{} to Blades of Ice": [
        "97,274"
    ],
    "+{} to Dragon Flight": [
        "97,275"
    ],
    "+{} to Death Sentry": [
        "97,276"
    ],
    "+{} to Blade Shield": [
        "97,277"
    ],
    "+{} to Venom": [
        "97,278"
    ],
    "+{} to Shadow Master": [
        "97,279"
    ],
    "+{} to Phoenix Strike": [
        "97,280"
    ],
    "+{} to not Consume Quantity": [
        "205"
    ]
}