import cv2
import os
import json
import pytest
from dataclasses import asdict
from d2r_image import processing
from d2r_image.data_models import GroundItemList
from common import ExpressionTest
from functools import cache
from pick_item_test_cases import NIP_PICK_TESTS
import nip.transpile as nip_transpile
from nip.actions import should_pickup
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
    for key, value in NIP_PICK_TESTS.items(): # key = basename, value = list[dict]
        for val in value: # for dict in list[dict]
            items_json: GroundItemList = load_ground_loot()[key]
            for ground_item in items_json.items:
                if ground_item.Text == val["Text"] and ground_item.Color == val["Color"]:
                    for expr in val["expressions"]:
                        expressions.append(ExpressionTest(
                            basename=key,
                            read_json=ground_item.as_dict(),
                            expression=expr[0],
                            keep_or_pick_expected=expr[1],
                            transpiled=nip_transpile.transpile_nip_expression(expr[0])
                        ))
                    break
    return expressions

@pytest.mark.parametrize('ground_items', load_ground_loot().items())
def test_ground_loot(ground_items: list[str, dict]):
    basename = ground_items[0]
    result = ground_items[1]
    x = open(f"{PATH}/{basename}.json").read()
    expected_properties = GroundItemList.from_json(x)
    # print(f"expected_properties: {expected_properties}")
    assert result == expected_properties


@pytest.mark.parametrize('should_pick_expression', expressions_test_list())
def test_pick_item(should_pick_expression: ExpressionTest, mocker):
    mocker.patch.object(nip_transpile, 'nip_expressions', [
        nip_transpile.load_nip_expression(should_pick_expression.expression)
    ])
    result, _ = should_pickup(should_pick_expression.read_json)
    if bool(result) != should_pick_expression.keep_or_pick_expected:
        print("\n")
        print(json.dumps(asdict(should_pick_expression), indent=4))
        print(f"should_pickup result: {result}; test pass/fail below")
        print("\n")
    assert bool(result) == should_pick_expression.keep_or_pick_expected
