import pytest
import os
import sys
sys.path.append (os.getcwd () + "/src")
from config import Config

class TestConfig:
    @pytest.mark.parametrize ("string, pickit_type, include, exclude, include_type",
    [
    ("0",0, [], [], "OR"), ("1",1, [], [], "OR"), ("2",2, [], [], "OR"),
    ("1, (AMAZONSKILLER, ASSASINSKILLER, BARBARIANSKILLER, DRUIDSKILLER, NECROMANCERSKILLER, PALADINSKILLER, SORCERESSSKILLER, (LIFE, 3_MAXIMUM_DAMAGE, ATTACK_RATING))",
        1,
        [["AMAZONSKILLER"], ["ASSASINSKILLER"], ["BARBARIANSKILLER"], ["DRUIDSKILLER"], ["NECROMANCERSKILLER"], ["PALADINSKILLER"], ["SORCERESSSKILLER"], ["LIFE", "3_MAXIMUM_DAMAGE", "ATTACK_RATING"]],
        [],
        "OR" 
    ),
    (
    "1, AND(15_INCREASED_ATTACK_SPEED, ENHANCED_DAMAGE)", 1, [["15_INCREASED_ATTACK_SPEED"], ["ENHANCED_DAMAGE"]], [],"AND"),
    ("1, SOCKETED_4, ETHEREAL", 1, [["SOCKETED_4"]], [["ETHEREAL"]], "OR"),
    ("1, 2_ASSASIN_SKILLS", 1, [["2_ASSASIN_SKILLS"]], [], "OR"),
    ("1, ENHANCED_DEFENSE, ETHEREAL", 1, [["ENHANCED_DEFENSE"]], [["ETHEREAL"]], "OR"),
    ("1, AND(LIGHTNING_RESIST, FIRE_RESIST, COLD_RESIST), ETHEREAL", 1, [["LIGHTNING_RESIST"], ["FIRE_RESIST"], ["COLD_RESIST"]], [["ETHEREAL"]], "AND"),
    ("1, AND(ENHANCED_DEFENSE, SOCKETED), (SOCKETED_1, SOCKETED_2)", 1, [["ENHANCED_DEFENSE"], ["SOCKETED"]], [["SOCKETED_1"], ["SOCKETED_2"]],"AND")
    ])
    def test_string_to_item_prop (self, string, pickit_type, include, exclude, include_type):
        cfg = Config()
        Itemprops = cfg.string_to_item_prop (string)
        assert (Itemprops.pickit_type == pickit_type)
        assert (Itemprops.include == include)
        assert (Itemprops.exclude == exclude)
        assert (Itemprops.include_type == include_type)
         
    def test_123 (self):
        print (os.getcwd()) 
        print (sys.path)