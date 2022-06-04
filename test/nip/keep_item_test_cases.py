NIP_KEEP_TESTS = {
    # monarch
    "D2R_0lR7EfbRGT": [
        (
            "[name] == Monarch && [quality] == magic && [flag] != ethereal # [sockets] >= 4 && [toblock] >= 20 && [fbr] >= 30",
            True
        ),
        (
            "[name] == Monarch && [quality] == magic && [flag] != ethereal # [defense] > 150",
            False
        ),
        (
            "[name] == Monarch && [quality] == magic",
            True
        ),
        (
            "[name] == Monarch && [flag] == ethereal",
            False
        ),
        (
            "[type] == anyshield",
            True
        ),
        (
            "[type] == shield",
            True
        ),
        (
            "[type] == assassinclaw",
            False
        ),
    ],
    # ettin axe
    "D2R_1HfJDuUXhe": [
        (
            "[name] == EttinAxe && [quality] == normal && [flag] == ethereal",
            True
        ),
        (
            "[type] == axe && [quality] == normal && [flag] == ethereal",
            True
        ),
        (
            "[type] == assassinclaw && [quality] == normal && [flag] == ethereal",
            False
        ),
        (
            "[type] == meleeweapon",
            True
        ),
    ],
    # rare bec-de-corbin
    "D2R_1ZMKfTQO7Q": [
        (
            "[name] == BecdeCorbin && [quality] == rare && [flag] != ethereal # [enhanceddamage] >= 61 && [tohit] >= 71 && [lightresist] >= 8 && [plusmindamage] >= 18 && [manaleech] >= 9 && [itemchargedskill] == 126",
            True
        ),
        (
            "[name] == BecdeCorbin # [enhanceddamage] >= 61",
            True
        ),
        (
            "[name] == BecdeCorbin # [tohit] >= 71",
            True
        ),
        (
            "[name] == BecdeCorbin # [plusmindamage] >= 18",
            True
        ),
        (
            "[name] == BecdeCorbin # [manaleech] >= 9",
            True
        ),
        (
            "[name] == BecdeCorbin # [enhanceddamage] >= 65",
            False
        ),
        (
            "[name] == BecdeCorbin # [lightresist] >= 8",
            True
        ),
        (
            "[name] == BecdeCorbin # [itemchargedskill] == 126",
            True
        ),
    ],
    # white phase blade
    "D2R_3BGDpVHQQS": [
        (
            "[name] == PhaseBlade && [quality] == normal && [flag] != ethereal",
            True
        ),
        (
            "[name] == PhaseBlade && [quality] == normal && [flag] == ethereal",
            False
        ),
        (
            "[name] == PhaseBlade && [quality] == normal",
            True
        ),
        (
            "[name] == PhaseBlade",
            True
        ),
        (
            "[type] == shield",
            False
        ),
    ],
    # shako
    "D2R_4IPy7u4fwt": [
        (
            "[Name] == Shako && [quality] == unique && [flag] != ethereal",
            True
        ),
        (
            "[Name] == Shako && [quality] == unique # [itemmagicbonus] > 51",
            False
        ),
        (
            "[Name] == Shako && [quality] == unique # [itemallskills] >= 2",
            True
        ),
        (
            "[Name] == Shako && [quality] == unique # [allstats] >= 2",
            True
        ),
        (
            "[Name] == Shako && [quality] == unique # [strength] == 2 && [dexterity] == 2 && [energy] == 2",
            True
        ),
            (
            "[Name] == Shako && [quality] == unique # [damageresist] == 10",
            True
        ),
    ],
    # rare ring
    "D2R_5vhnOkej0W": [
        (
            "[name] == Ring && [quality] == rare && [flag] != ethereal # [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 44 && [itemmagicbonus] >= 10 && [lightresist] >= 30 && [dexterity] >= 15 && [fcr] >= 10 && [maxhp] >= 40",
            True
        ),
        (
            "[name] == Ring && [quality] == rare # [itemmagicbonus] >= 10 && [dexterity] >= 15 && [fcr] >= 10 && [maxhp] >= 40",
            True
        ),
        (
            "[name] == Ring && [quality] == rare # [lightresist] >= 30 && [maxhp] >= 40",
            True
        ),
        (
            "[name] == Ring && [quality] == rare && [flag] == ethereal",
            False
        ),
        (
            "[name] == Ring && [quality] == unique",
            False
        ),
    ],
    # magic feral claws
    "D2R_6AHfXLJO4l": [
        (
            "[name] == FeralClaws && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [ias] >= 40 && [skillLightningSentry] >= 3 && [skillDeathSentry] >= 3 && [skillFade] >= 3",
            True
        ),
        (
            "[name] == FeralClaws && [quality] == magic && [flag] != ethereal",
            True
        ),
        (
            "[name] == FeralClaws # [itemaddskilltab] >= 4",
            False
        ),
        (
            "[name] == FeralClaws && [quality] == magic && [flag] != ethereal # [ias] >= 40",
            True
        ),
        (
            "[name] == FeralClaws && [quality] == magic && [flag] != ethereal # [ias] >= 41",
            False
        ),
        (
            "[type] == assassinclaw && [class] == elite",
            True
        ),
        (
            "[type] == assassinclaw && [class] == exceptional",
            False
        ),
    ],
    # rare cantor trophy
    "D2R_7CAuD9VcLh": [
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [itemaddskilltab] >= 2 && [itemarmorperlevel] >= 4 && [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80 && [itemreplenishdurability] >= 1 && [poisonmindam] >= 13 && [poisonmaxdam] >= 28 && [skillBoneSpirit] >= 3 && [skillBoneSpear] >= 3 && [skillBoneWall] >= 3",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [skillBoneSpear] >= 3 && [skillBoneWall] >= 3",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [itemaddskilltab] >= 2",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [itemreplenishdurability] >= 1",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [poisonmindam] >= 13 && [poisonmaxdam] >= 28",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [allres] >= 20",
            True
        ),
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [allres] >= 21",
            False
        ),
    ],
    # magic matriarchal spear
    "D2R_7ov1FGVkvQ": [
        (
            "[name] == MatriarchalSpear && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 6 && [ias] >= 40",
            True
        ),
        (
            "[type] == amazonspear",
            True
        ),
    ],
    # rare arbalest
    "D2R_7wqOnPKCxN": [
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [coldmindam] >= 35 && [coldmaxdam] >= 116 && [lightresist] >= 26 && [poisonmindam] >= 150 && [plusmaxdamage] >= 1 && [lightmindam] >= 1 && [lightmaxdam] >= 29 && [itemchargedskill] == 12",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [coldmindam] >= 35 && [coldmaxdam] >= 116",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [plusmaxdamage] >= 1",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [lightmindam] >= 1 && [lightmaxdam] >= 29 && [itemchargedskill] == 12",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [itemchargedskill] == 12",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal",
            True
        ),
        (
            "[name] == Arbalest && [quality] == rare && [flag] != ethereal # [poisonmindam] >= 150",
            True
        ),
    ],
    # giant thresher eth
    "D2R_60FdSnzNbq": [
        (
            "[name] == GiantThresher && [quality] <= superior && [flag] == ethereal",
            True
        ),
    ],
    # blue mighty scepter
    "D2R_65KHCMvsK6": [
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [fcr] >= 10 && [skillHolyShock] >= 3 && [skillFistoftheHeavens] >= 3 && [skillConviction] >= 3",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [fcr] >= 10",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [skillHolyShock] >= 3 && [skillFistoftheHeavens] >= 3 && [skillConviction] >= 3",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [skillHolyShock] >= 3",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [skillFistoftheHeavens] >= 3",
            True
        ),
        (
            "[name] == MightyScepter && [quality] == magic && [flag] != ethereal # [skillConviction] >= 3",
            True
        ),
    ],
    # riphook
    "D2R_a6D8Kmv3uT": [
        (
            "[Name] == Razorbow && [quality] == unique # [enhanceddamage] >= 220 && [lifeleech] >= 10",
            True
        ),
        (
            "[Name] == Razorbow && [quality] == unique # [lifeleech] >= 10",
            True
        ),
        (
            "[Name] == Razorbow && [quality] == unique # [enhanceddamage] >= 220",
            True
        ),
    ],
    # white unearthed wand
    "D2R_ARmKCSdJnI": [
        (
            "[Name] == UnearthedWand && [quality] == normal && [flag] != ethereal",
            True
        ),
    ],
    # chance guards
    "D2R_AUakVcxMGp": [
        (
            "[name] == ChainGloves && [quality] == unique # [itemgoldbonus] >= 200 && [itemmagicbonus] >= 40",
            True
        ),
    ],
    # rare archon staff
    "D2R_bE0gVUl4R7": [
        (
            "[name] == ArchonStaff && [quality] == rare && [flag] != ethereal # [sorceressskills] >= 2 && [maxmana] >= 76 && [itemdamagetomana] >= 10 && [energy] >= 20 && [ias] >= 20 && [fcr] >= 20 && [skillGlacialSpike] >= 3 && [skillFrozenOrb] >= 3 && [skillColdMastery] >= 3",
            True
        ),
    ],
    # rare amulet
    "D2R_cCgyl3NTq9": [
        (
            "[name] == Amulet && [quality] == rare && [flag] != ethereal # [fireresist] >= 10 && [coldresist] >= 30 && [itemmagicbonus] >= 10 && [itempoisonlengthresist] >= 25 && [magicdamagereduction] >= 3 && [fcr] >= 10",
            True
        ),
    ],
    # rare amulet
    "D2R_cCgyl3NTq9": [
        (
            "[name] == Amulet && [quality] == rare && [flag] != ethereal # [fireresist] >= 10 && [coldresist] >= 30 && [itemmagicbonus] >= 10 && [itempoisonlengthresist] >= 25 && [magicdamagereduction] >= 3 && [fcr] >= 10",
            False
        ),
        (
            "[name] == Amulet && [quality] == rare && [flag] != ethereal # [sorceressskills] >= 2 && [itemdamagetomana] >= 12 && [maxmana] >= 90 && [fcr] >= 10 && [strength] >= 26 && [energy] >= 20",
            True
        ),
    ],
    # white flail
    "D2R_cPszZcBC81": [
        (
            "[name] == Flail && [quality] == normal && [flag] != ethereal",
            True
        ),
    ],
    # white large siege bow
    "D2R_d7clAOFrFY": [
        (
            "[name] == LargeSiegeBow && [quality] == normal && [flag] != ethereal",
            True
        ),
    ],
    # magic gladius
    "D2R_DaDAU5n7GJ": [
        (
            "[name] == Gladius && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [strength] >= 2",
            True
        ),
    ],
    # rare ancient axe
    "D2R_dvAVQGnYzc": [
        (
            "[name] == AncientAxe && [quality] == rare && [flag] == ethereal # [enhanceddamage] >= 350 && [tohit] >= 550 && [ias] >= 40 && [plusmaxdamage] >= 20 && [itemreplenishdurability] >= 1",
            True
        ),
    ],
    # magic lich wand
    "D2R_DyLF3Fj0FK": [
        (
            "[name] == LichWand && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [fcr] >= 20 && [skillBoneSpirit] >= 3 && [skillBoneWall] >= 3 && [skillBoneSpear] >= 3",
            True
        ),
    ],
    # magic cloudy sphere
    "D2R_EYVbkOSvLp": [
        (
            "[name] == CloudySphere && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [fcr] >= 20 && [skillNova] >= 3 && [skillLightningMastery] >= 3 && [skillEnergyShield] >= 3",
            True
        ),
    ],
    # white lochaber axe
    "D2R_fBh9PdCvNz": [
        (
            "[name] == LochaberAxe && [quality] == normal && [flag] != ethereal",
            True
        ),
    ],
    # rare amulet
    "D2R_gE6A96ftDw": [
        (
            "[name] == Amulet && [quality] == rare && [flag] != ethereal # [sorceressskills] >= 2 && [itemdamagetomana] >= 12 && [maxmana] >= 90 && [fcr] >= 10 && [strength] >= 26 && [energy] >= 20",
            False
        ),
        (
            "[name] == Amulet && [quality] == rare && [flag] != ethereal # [fireresist] >= 10 && [coldresist] >= 30 && [itemmagicbonus] >= 10 && [itempoisonlengthresist] >= 25 && [magicdamagereduction] >= 3 && [fcr] >= 10",
            True
        ),
    ],
    # rare archon plate
    "D2R_Ghwf32hhjz": [
        (
            "[name] == ArchonPlate && [quality] == rare && [flag] != ethereal # [coldresist] >= 26 && [fireresist] >= 26 && [lightresist] >= 26 && [hpregen] >= 5 && [dexterity] >= 8 && [strength] >= 18",
            True
        ),
    ],
    # ormus robes
    "D2R_gIVrKehVNq": [
        (
            "[name] == DuskShroud && [quality] == unique # [fcr] >= 20 && [Passivecoldmastery] >= 15 && [Skillfrozenorb] >= 3",
            True
        ),
    ],
    # rare ceremonial javelin
    "D2R_GOnpYcQ539": [
        (
            "[name] == CeremonialJavelin && [quality] == rare && [flag] != ethereal # [enhanceddamage] >= 300 && [amazonskills] >= 2 && [itemmaxdamageperlevel] >= 1 && [itemtohitperlevel] >= 1 && [itemskillonhit] == 66 && [strength] >= 15 && [ias] >= 40 && [itemaddskilltab] >= 2",
            True
        ),
    ],
    # magic grand matron bow
    "D2R_gxlIdIHuBX": [
        (
            "[name] == GrandMatronBow && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 6 && [ias] >= 20",
            True
        ),
    ],
    # magic rondache
    "D2R_gZNEsYkfkj": [
        (
            "[name] == Rondache && [quality] == magic && [flag] != ethereal # [sockets] >= 4 && [toblock] >= 20 && [fbr] >= 30",
            True
        ),
    ],
    # rare battle belt
    "D2R_h8bXDXTwYm": [
        (
            "[name] == BattleBelt && [quality] == rare && [flag] != ethereal # [lightresist] >= 30 && [fireresist] >= 30 && [maxmana] >= 20 && [fhr] >= 24 && [itemgoldbonus] >= 80 && [strength] >= 30",
            True
        ),
    ],
    # crown of ages
    "D2R_HPHrNWjUkD": [
        (
            "[Name] == Corona && [quality] == unique # [sockets] >= 2 && [damageresist] >= 15",
            True
        ),
    ],
    # magic gladius
    "D2R_HyHbbZZA1n": [
        (
            "[name] == Gladius && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [itemchargedskill] == 36",
            True
        ),
    ],
    # reaper's toll
    "D2R_I5LbjVIYvy": [
        (
            "[name] == Thresher && [quality] == unique # [enhanceddamage] >= 220",
            True
        ),
    ],
    # magic akaran targe
    "D2R_iEAZAhsn0m": [
        (
            "[name] == AkaranTarge && [quality] == magic && [flag] != ethereal # [sockets] >= 4 && [toblock] >= 20 && [fbr] >= 30 && [tohit] >= 111 && [enhanceddamage] >= 58",
            True
        ),
    ],
    # rare akaran rondache
    "D2R_j91F4T3G0M": [
        (
            "[name] == AkaranRondache && [quality] == rare && [flag] != ethereal # [enhanceddefense] >= 200 && [sockets] >= 2 && [itemdamagetomana] >= 12 && [normaldamagereduction] >= 7 && [itemreplenishdurability] >= 1 && [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 120",
            True
        ),
    ],
    # rare ancient armor
    "D2R_jdSojrLyHn": [
        (
            "[name] == AncientArmor && [quality] == rare && [flag] != ethereal # [itemarmorperlevel] >= 24 && [sockets] >= 2 && [fireresist] >= 10 && [dexterity] >= 3 && [normaldamagereduction] >= 3 && [fhr] >= 24",
            True
        ),
    ],
    # swordback hold
    "D2R_jiUGpeejOO": [
        (
            "[Name] == Spikedshield && [quality] == unique && [flag] != ethereal # [enhanceddefense] >= 60",
            True
        ),
    ],
    # white cedar staff
    "D2R_JKj1ONC0Qo": [
        (
            "[name] == CedarStaff && [quality] == normal && [flag] != ethereal",
            True
        ),
    ],
    # rare alpha helm
    "D2R_JOTQPzIIre": [
        (
            "[name] == AlphaHelm && [quality] == rare && [flag] != ethereal # [itemtohitpercentperlevel] >= 2 && [enhanceddefense] >= 200 && [maxmana] >= 5 && [itempoisonlengthresist] >= 25 && [maxhp] >= 40 && [itemreplenishdurability] >= 1 && [skillVolcano] >= 3 && [skillFissure] >= 3 && [skillArmageddon] >= 3",
            True
        ),
    ],
    # rare alpha helm
    "D2R_JOTQPzIIre": [
        (
            "[name] == AlphaHelm && [quality] == rare && [flag] != ethereal # [itemtohitpercentperlevel] >= 2 && [enhanceddefense] >= 200 && [maxmana] >= 5 && [itempoisonlengthresist] >= 25 && [maxhp] >= 40 && [itemreplenishdurability] >= 1 && [skillVolcano] >= 3 && [skillFissure] >= 3 && [skillArmageddon] >= 3",
            True
        ),
    ],
    # rare antlers
    "D2R_JxJMLkkrcO": [
        (
            "[name] == Antlers && [quality] == rare && [flag] != ethereal # [druidskills] >= 2 && [sockets] >= 2 && [enhanceddefense] >= 100 && [energy] >= 9 && [maxhp] >= 36 && [fhr] >= 10 && [skillCycloneArmor] >= 3 && [skillRabies] >= 3 && [skillFeralRage] >= 3",
            True
        ),
    ],
    # magic long staff
    "D2R_jYVm7kYbXA": [
        (
            "[name] == LongStaff && [quality] == magic && [flag] != ethereal # [sorceressskills] >= 2 && [fcr] >= 20 && [skillFireMastery] >= 3 && [skillMeteor] >= 3 && [skillFireBall] >= 3",
            True
        ),
    ],
    # valkyrie wing
    "D2R_K0SM6iiTyD": [
        (
            "[name] == WingedHelm && [quality] == unique # [enhanceddefense] >= 200",
            True
        ),
    ],
    # magic fury visor
    "D2R_LsXL0Ym8Ys": [
        (
            "[name] == FuryVisor && [quality] == magic && [flag] != ethereal # [barbarianskills] >= 2 && [maxhp] >= 36 && [skillBattleOrders] >= 3 && [skillWarCry] >= 3 && [skillBattleCommand] >= 3",
            True
        ),
    ],
    # magic ring
    "D2R_lVJEBucdd8": [
        (
            "[name] == Ring && [quality] == magic && [flag] != ethereal # [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 60 && [fcr] >= 10",
            True
        ),
        (
            "[name] == Ring && [quality] == magic && [flag] != ethereal # [allres] >= 15 && [fcr] >= 10",
            True
        ),
        (
            "[name] == Ring && [quality] == magic && [flag] != ethereal # [allres] >= 16 && [fcr] >= 10",
            False
        ),
    ],
    # magic maiden javelin
    "D2R_MJjAgKQABC": [
        (
            "[name] == MaidenJavelin && [quality] == magic && [flag] != ethereal # [amazonskills] >= 2 && [ias] >= 40 && [itemaddskilltab] >= 3",
            True
        ),
    ],
    # rare ancient sword
    "D2R_MnN9IaI0NA": [
        (
            "[name] == AncientSword && [quality] == rare && [flag] != ethereal # [itemaddskilltab] >= 1 && [itemundeadtohit] >= 126 && [itemundeaddamagepercent] >= 101 && [tohit] >= 201 && [enhanceddamage] >= 126 && [ias] >= 40 && [firemindam] >= 15 && [firemaxdam] >= 48 && [itemchargedskill] == 144",
            True
        ),
    ],
    # magic eldritch orb
    "D2R_MTB3TGtfgu": [
        (
            "[name] == EldritchOrb && [quality] == magic && [flag] != ethereal # [maxmana] >= 186 && [fcr] >= 20 && [skillEnergyShield] >= 3 && [skillLightningMastery] >= 3 && [skillChainLightning] >= 3",
            True
        ),
    ],
    # rare eth blade talons
    "D2R_O0WUcFkvIA": [
        (
            "[name] == BladeTalons && [quality] == rare && [flag] == ethereal # [enhanceddamage] >= 350 && [tohit] >= 550 && [ias] >= 40 && [itemreplenishdurability] >= 1 && [plusmaxdamage] >= 20",
            True
        ),
        (
            "[name] == BladeTalons && [quality] == rare && [flag] != ethereal",
            False
        ),
    ],
    # magic coronet
    "D2R_o1NZtzmhmF": [
        (
            "[name] == Coronet && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [fcr] >= 20",
            True
        ),
    ],
    # magic griffon headdress
    "D2R_OYgwehN2Ah": [
        (
            "[name] == GriffonHeaddress && [quality] == magic && [flag] != ethereal # [sockets] >= 3 && [maxhp] >= 40 && [skillVolcano] >= 3 && [skillFissure] >= 3 && [skillArmageddon] >= 3",
            True
        ),
    ],
    # doombringer champion sword
    "D2R_PTvvNUuaHq": [
        (
            "[name] == ChampionSword && [quality] == unique # [enhanceddamage] >= 220",
            True
        ),
    ],
    # magic socketed diadem
    "D2R_q45vGxNCeu": [
        (
            "[name] == Diadem && [quality] == magic && [flag] != ethereal # [sockets] >= 2 && [fcr] >= 20",
            True
        ),
        (
            "[name] == Diadem && [quality] == magic && [flag] != ethereal # [sockets] >= 3",
            False
        ),
    ],
    # rare ancient shield
    "D2R_QJo13V7ET2": [
        (
            "[name] == AncientShield && [quality] == rare && [flag] != ethereal # [enhanceddefense] >= 100 && [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80 && [itemaddskilltab] >= 1 && [itemskillongethit] == 48 && [toblock] >= 20 && [fbr] >= 30 && [itemreplenishdurability] >= 1",
            True
        ),
        (
            "[name] == AncientShield && [quality] == rare && [flag] != ethereal # [itemskillongethit] == 48",
            True
        ),
        (
            "[name] == AncientShield && [quality] == rare && [flag] != ethereal # [fbr] >= 30",
            True
        ),
        (
            "[name] == AncientShield && [quality] == rare && [flag] != ethereal # [toblock] >= 20",
            True
        ),
        (
            "[name] == AncientShield && [quality] == rare && [flag] != ethereal # [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80",
            True
        ),
        (
            "[type] == assassinclaw",
            False
        ),
    ],
    # wizardspike
    "D2R_qwgERVLYvQ": [
        (
            "[Name] == BoneKnife && [quality] == unique # [fcr] >= 50",
            True
        ),
    ],
    # magic preserved head
    "D2R_tB0MNZqKsc": [
        (
            "[name] == PreservedHead && [quality] == magic && [flag] != ethereal # [sockets] >= 2 && [toblock] >= 20 && [fbr] >= 30 && [skillIronGolem] >= 3 && [skillPoisonNova] >= 3 && [skillPoisonExplosion] >= 3",
            True
        ),
        (
            "[type] == necromanceritem",
            True
        ),
        (
            "[type] == amazonitem",
            False
        ),
    ],
    # magic heavy bracers
    "D2R_UIyDDtROVY": [
        (
            "[name] == HeavyBracers && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [ias] >= 20",
            True
        ),
    ],
    # magic hydra bow
    "D2R_URqU8bUiyv": [
        (
            "[name] == HydraBow && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 3 && [ias] >= 20",
            True
        ),
    ],
    # hellslayer
    "D2R_V4HkMaiIiI": [
        (
            "[name] == Decapitator && [quality] == unique && [flag] != ethereal # [enhanceddamage] >= 100",
            True
        ),
    ],
    # rare cantor trophy
    "D2R_w7DvFnRl6c": [
        (
            "[name] == CantorTrophy && [quality] == rare && [flag] == ethereal # [itemaddskilltab] >= 2 && [itemarmorperlevel] >= 4 && [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80 && [toblock] >= 10 && [fbr] >= 15 && [itemreplenishdurability] >= 1 && [itemhalffreezeduration] >= 1 && [skillBoneSpirit] >= 3 && [skillBoneSpear] >= 3 && [skillBoneWall] >= 3",
            True
        ),
        (
            "[name] == CantorTrophy # [itemaddskilltab] >= 2 && [itemarmorperlevel] >= 4",
            True
        ),
        (
            "[name] == CantorTrophy # [fireresist]+[coldresist]+[lightresist]+[poisonresist] >= 80",
            True
        ),
        (
            "[name] == CantorTrophy # [toblock] >= 10 && [fbr] >= 15",
            True
        ),
        (
            "[name] == CantorTrophy # [itemreplenishdurability] >= 1 && [itemhalffreezeduration] >= 1",
            True
        ),
        (
            "[name] == CantorTrophy # [skillBoneSpirit] >= 3 && [skillBoneSpear] >= 3 && [skillBoneWall] >= 3",
            True
        ),
    ],
    # magic ballista
    "D2R_wASxol7GDr": [
        (
            "[name] == Ballista && [quality] == magic && [flag] != ethereal # [poisonresist] >= 26 && [itemchargedskill] == 6",
            True
        ),
    ],
    # magefist
    "D2R_wYl0iQwct8": [
        (
            "[name] == LightGauntlets && [quality] == unique # [fcr] >= 20",
            True
        ),
    ],
    # magic ghost glaive
    "D2R_XmiUAD2hC6": [
        (
            "[name] == GhostGlaive && [quality] == magic && [flag] == ethereal # [enhanceddamage] >= 300 && [itemreplenishquantity] >= 1",
            True
        ),
    ],
    # 4os eth cryptic axe
    "D2R_Xmiw3PsbcD": [
        (
            "[name] == CrypticAxe && [quality] == normal && [flag] == ethereal",
            True
        ),
        (
            "[name] == CrypticAxe && [quality] == normal # [sockets] >= 4",
            True
        ),
        (
            "[name] == CrypticAxe && [quality] == normal && [flag] == ethereal # [sockets] >= 4",
            True
        ),
    ],
    # vampgaze
    "D2R_xP50v8yBqQ": [
        (
            "[name] == GrimHelm && [quality] == unique # [lifeleech] >= 8 && [manaleech] >= 8",
            True
        ),
    ],
    # andys
    "D2R_Xq0aFuN5cj": [
        (
            "[name] == Demonhead && [quality] == unique # [ias] >= 20",
            True
        ),
    ],
    # superior mancatcher
    "D2R_YhXVS8Q4j6": [
        (
            "[name] == ManCatcher && [quality] == superior",
            True
        ),
        (
            "[name] == ManCatcher && [quality] == normal",
            False
        ),
    ],
    # rare bone wand
    "D2R_ZI6fzNFd3E": [
        (
            "[name] == BoneWand && [quality] == rare && [flag] != ethereal # [sockets] >= 2 && [maxmana] >= 76 && [necromancerskills] >= 2 && [fcr] >= 20 && [hpregen] >= 5 && [energy] >= 20 && [skillBoneSpirit] >= 3 && [skillIronGolem] >= 3 && [skillBoneSpear] >= 3",
            True
        ),
        (
            "[name] == BoneWand # [necromancerskills] >= 2",
            True
        ),
        (
            "[name] == BoneWand # [hpregen] >= 5 && [energy] >= 20",
            True
        ),
        (
            "[name] == BoneWand # [skillBoneSpirit] >= 3 && [skillIronGolem] >= 3 && [skillBoneSpear] >= 3",
            True
        ),
        (
            "[name] == BoneWand # [skillBoneSpirit] >= 3",
            True
        ),
        (
            "[name] == BoneWand # [skillIronGolem] >= 3",
            True
        ),
        (
            "[name] == BoneWand # [skillBoneSpear] >= 3",
            True
        ),
    ],
    # griffs
    "D2R_zKf6cKX5gZ": [
        (
            "[Name] == Diadem && [quality] == unique && [flag] != ethereal",
            True
        ),
    ],
    # rare battle boots
    "D2R_ZtRedtGBPB": [
        (
            "[name] == BattleBoots && [quality] == rare && [flag] != ethereal # [fireresist] >= 40 && [lightresist] >= 40 && [enhanceddefense] >= 200 && [fhr] >= 10 && [frw] >= 30 && [itemgoldbonus] >= 80",
            True
        ),
    ],
    # sorc torch
    "hovered_item_20220504_160228": [
        (
            "[name] == largecharm && [quality] == unique # [itemaddsorceressskills] == 3 && [allstats] >= 10 && [allres] >= 10",
            True
        ),
    ],
    # carrion wind
    "hovered_item_20220504_160419": [
        (
            "[type] == ring && [quality] == unique # [lifeleech] >= 8 // carrion wind",
            True
        ),
    ],
    # burning essence of terror
    "hovered_item_20220504_161113": [
        (
            "[Name] == Burningessenceofterror",
            True
        ),
        (
            "[Type] == quest",
            True
        ),
    ],
    # thul rune
    "hovered_item_20220504_161131": [
        (
            "[Name] == Thulrune",
            True
        ),
        (
            "[Type] == rune",
            True
        ),
        (
            "[name] >= eldrune",
            True
        ),
    ],
    # tal helm
    "hovered_item_20220504_161338": [
        (
            "[Name] == Deathmask && [Quality] == Set",
            True
        ),
        (
            "[Name] == Deathmask # [defense] >= 100",
            True
        ),
    ],
    # unidentified rare ring
    "positional_ring": [
        (
            "[Name] == ring && [Quality] == rare",
            True
        ),
    ],
    # magic jewel
    "hovered_item_20220504_161003": [
        (
            "[Name] == jewel && [Quality] == magic # [ias] >= 15 && [enhanceddamage] >= 15",
            True
        ),
    ],
    # magic large charm
    "D2R_0tY8VkpM8T": [
        (
            "[name] == LargeCharm && [quality] == magic && [flag] != ethereal # [plusmaxdamage] >= 2 && [fhr] >= 8",
            True
        ),
    ],
    # rare jewel
    "D2R_1Iu96WxakK": [
        (
            "[name] == Jewel && [quality] == rare && [flag] != ethereal # [plusmindamage] >= 7 && [maxmana] >= 13 && [poisonresist] >= 23 && [lightmindam] >= 1 && [lightmaxdam] >= 81",
            True
        ),
    ],
    # rare jewel
    "D2R_3sLDs3uUMd": [
        (
            "[name] == Jewel && [quality] == magic && [flag] != ethereal # [itemundeadtohit] >= 30 && [itemundeaddamagepercent] >= 38 && [strength] >= 3",
            True
        ),
    ],
    # magic grand charm
    "D2R_Z7AVNV8X27": [
        (
            "[name] == GrandCharm && [quality] == magic && [flag] != ethereal # [itemaddskilltab] == 1 && [lightmindam] >= 1 && [lightmaxdam] >= 3",
            True
        ),
        (
            "[name] == GrandCharm && [quality] == magic && [flag] != ethereal # [itemaddskilltab] >= 1",
            True
        ),
        (
            "[name] == GrandCharm && [quality] == magic && [flag] != ethereal # [passiveandmagicskilltab] >= 1",
            True
        ),
        (
            "[name] == GrandCharm && [quality] == magic && [flag] != ethereal # [passiveandmagicskilltab] >= 5",
            False
        ),
    ],
    # magic large charm
    "D2R_Y0YlR268P3": [
        (
            "[name] == LargeCharm && [quality] == magic && [flag] != ethereal # [itemmagicbonus] >= 6 && [frw] >= 5",
            True
        ),
    ],
    # magic jewel
    "D2R_aOyb5TqkIm": [
        # poison calculation??
        (
            "[name] == Jewel && [quality] == magic && [flag] != ethereal # [lightresist] >= 23 && [poisonmindam] >= 103",
            True
        ),
        (
            "[name] == Jewel && [quality] == magic && [flag] != ethereal # [lightresist] >= 23 && [poisonmindam] >= 20",
            True
        ),
        (
            "[name] == Jewel && [quality] == magic && [flag] != ethereal # [lightresist] >= 23",
            True
        ),
    ],
    # magic grand charm
    "D2R_aXKcy7ITEB": [
        (
            "[name] == GrandCharm && [quality] == magic && [flag] != ethereal # [defense] >= 47",
            True
        ),
    ],
    # magic small charm
    "D2R_KKoeMHxUsp": [
        (
            "[name] == SmallCharm && [quality] == magic && [flag] != ethereal # [plusmaxdamage] >= 1 && [frw] >= 3",
            True
        ),
    ],
    # rare jewel
    "D2R_lYkkSS0qCi": [
        (
            "[name] == Jewel && [quality] == rare && [flag] != ethereal # [itemlightradius] >= 1 && [tohit] >= 10 && [strength] >= 8 && [coldmindam] >= 1 && [coldmaxdam] >= 4 && [firemindam] >= 7 && [firemaxdam] >= 21",
            True
        ),
    ],
    # rare jewel
    "D2R_vBBOGsinxA": [
        (
            "[name] == Jewel && [quality] == rare && [flag] != ethereal # [itemundeadtohit] >= 38 && [itemundeaddamagepercent] >= 38 && [strength] >= 3 && [itemmagicbonus] >= 8 && [itemreqpercent] <= -15",
            True
        ),
    ],
    # rainbow facet, poison
    "D2R_nLSBZYixOe": [
        (
            "[Name] == jewel && [quality] == unique # [passivecoldpierce]+[passivecoldmastery] >= 10 || [passivepoispierce]+[passivepoismastery] >= 10 || [passiveltngpierce]+[passiveltngmastery] >= 10 || [passivefirepierce]+[passivefiremastery] >= 10",
            True
        ),
        (
            "[Name] == jewel && [quality] == unique # [passivepoispierce]+[passivepoismastery] >= 10",
            True
        ),
    ],
    # rainbow facet, fire
    "D2R_5ctnVauZr1": [
        (
            "[Name] == jewel && [quality] == unique # [passivefirepierce]+[passivefiremastery] >= 10",
            True
        ),
    ],
}