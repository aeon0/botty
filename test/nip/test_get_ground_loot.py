import cv2
import os
import json
import pytest
from dataclasses import asdict
from d2r_image import processing
from d2r_image.data_models import GroundItemList
from common import ExpressionTest, pretty_dict
from functools import cache
from pick_item_test_cases import BNIP_PICK_TESTS
from bnip.transpile import generate_expression_object, transpile_bnip_expression
import bnip.actions as bnip_actions
import screen
import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called

PATH='test/assets/ground_loot'
screen.set_window_position(0, 0)

@cache
def load_ground_loot() -> dict:
    test_objs = {}
    for filename in os.listdir(PATH):
        filename = filename
        if filename.lower().endswith('.png'):
            basename = filename[:-4]
            image = cv2.imread(f"{PATH}/{basename}.png")
            test_objs[basename] = processing.get_ground_loot(image)
    return test_objs

@cache
def expressions_test_list() -> list[ExpressionTest]:
    expressions = []
    for key, value in BNIP_PICK_TESTS.items(): # key = basename, value = list[dict]
        for val in value: # for dict in list[dict]
            items_json: GroundItemList = load_ground_loot()[key]
            for ground_item in items_json.items:
                if ground_item.Text == val["Text"] and ground_item.Color == val["Color"]:
                    for expr in val["expressions"]:
                        expressions.append(ExpressionTest(
                            basename=key,
                            read_json=ground_item.as_dict(),
                            expression=expr["expression"],
                            pick_expected=expr["should_pickup"],
                            transpiled=transpile_bnip_expression(expr["expression"])
                        ))
                    break
    return expressions

# this test has essentially been made obsolete by the nip should_pick() tests

# @pytest.mark.parametrize('ground_items', load_ground_loot().items())
# def test_ground_loot(ground_items: list[str, dict]):
#     basename = ground_items[0]
#     result = ground_items[1]
#     x = open(f"{PATH}/{basename}.json").read()
#     expected_properties = GroundItemList.from_json(x)
#     # print(f"expected_properties: {expected_properties}")
#     assert result == expected_properties


@pytest.mark.parametrize('should_pick_expression', expressions_test_list())
def test_pick_item(should_pick_expression: ExpressionTest, mocker):
    mocker.patch.object(bnip_actions, 'bnip_expressions', [
        generate_expression_object(should_pick_expression.expression)
    ])
    result, matching_expression = bnip_actions.should_pickup(should_pick_expression.read_json)
    if bool(result) != should_pick_expression.pick_expected:
        print("\n")
        print("bnip_expressions object:")
        print(pretty_dict(asdict(bnip_actions.bnip_expressions[0])))
        print("test expression object:")
        print(json.dumps(asdict(should_pick_expression), indent=4))
        if matching_expression:
            print(f"matching expression: {matching_expression}")
        print(f"should_pickup() result: {result}; test pass/fail below")
        print("\n")
    assert bool(result) == should_pick_expression.pick_expected
