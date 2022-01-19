import pytest
from config import Config

class TestConfig:
    @pytest.mark.parametrize ("string, pickit_type, include, exclude, include_type",
    [
    ("0",0, None, None), ("1",1, None, None), ("2",2, None, None),
    ("1, (Amazonskiller, Assasinskiller, Barbarianskiller, Druidskiller, Necromancerskiller, Paladinskiller, Sorceressskiller, (Life, 3_maximum_damage, attack_rating))",
        1,
        ["AMAZONSKILLER", "ASSASINSKILLER", "BARBARIANSKILLER", "DRUIDSKILLER", "NECROMANCERSKILLER", "PALADINSKILLER", "SORCERESSSKILLER", ["LIFE", "3_MAXIMUM_DAMAGE", "ATTACK_RATING"]],
        None,
        "OR" 
    ),
    (
    "1, and(15_increased_attack_speed, enhanced_damage)", 1, ["15_INCREASED_ATTACK_SPEED", "ENHANCED_DAMAGE"], None,"AND"),
    ("1, socketed_4, ethereal", 1, ["SOCKETED_4"], ["ETHEREAL"]),
    ("1, 2_assasin_skills", 1, ["2_ASSASIN_SKILLS"], None, "OR"),
    ("0,, ethereal", 0, None, ["ETHEREAL"], "OR"),
    ("1, and(lightning_resist, fire_resist, cold_resist), ethereal", 1, ["LIGHTNING_RESIST", "FIRE_RESIST", "COLD_RESIST"], ["ETHEREAL"], "AND"),
    ("1, and(enhanced_defense, socketed), (socketed_1, socketed_2)", 1, ["ENHANCED_DEFENSE", "SOCKETED"], ["SOCKETED_1", "SOCKETED_2"],"AND")
    ])
    def test_parse_item_config_string (self, string, pickit_type, include, exclude, include_type):
        cfg = Config()
        Itemprops = cfg.parse_item_config_string (string)
        assert (Itemprops.pickit_type == pickit_type)
        assert (Itemprops.include == include)
        assert (Itemprops.exclude == exclude)
        assert (Itemprops.include_type == include_type)