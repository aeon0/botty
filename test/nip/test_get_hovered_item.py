import os
import cv2
import json
from dataclasses import asdict
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem
from functools import cache
from keep_item_test_cases import BNIP_KEEP_TESTS
from common import ExpressionTest, pretty_dict
import screen
import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called
from bnip.transpile import generate_expression_object, transpile_bnip_expression
import bnip.actions as bnip_actions


PATH='test/assets/hovered_items'
screen.set_window_position(0, 0)

@cache
def load_hovered_items() -> dict:
    test_objs = {}
    for filename in os.listdir(PATH):
        filename = filename
        if filename.lower().endswith('.png'):
            basename = filename[:-4]
            image = cv2.imread(f"{PATH}/{basename}.png")
            result, _ = processing.get_hovered_item(image)
            test_objs[basename] = result
    return test_objs

@cache
def expressions_test_list() -> list[ExpressionTest]:
    expressions = []
    for key, value in BNIP_KEEP_TESTS.items():
        for val in value:
            expressions.append(ExpressionTest(
                basename=key,
                read_json=load_hovered_items()[key].as_dict(),
                expression=val["expression"],
                keep_expected=val["should_keep"],
                id_expected=None if not "should_id" in val else val["should_id"],
                transpiled=transpile_bnip_expression(val["expression"])
            ))
    return expressions

# this test has essentially been made obsolete by the bnip should_keep() tests

# @pytest.mark.parametrize('hovered_item', load_hovered_items().items())
# def test_hovered_item(hovered_item: list[str, dict]):
#     basename = hovered_item[0]
#     result = hovered_item[1]
#     expected_properties = HoveredItem.from_json(open(f"{PATH}/{basename}.json").read())
#     assert result == expected_properties

@pytest.mark.parametrize('should_keep_expression', expressions_test_list())
def test_keep_item(should_keep_expression: ExpressionTest, mocker):
    mocker.patch.object(bnip_actions, 'bnip_expressions', [
        generate_expression_object(should_keep_expression.expression)
    ])
    result, matching_expression = bnip_actions.should_keep(should_keep_expression.read_json)
    if bool(result) != should_keep_expression.keep_expected:
        print("\n")
        print("bnip_expressions object:")
        print(pretty_dict(asdict(bnip_actions.bnip_expressions[0])))
        print("test expression object:")
        print(json.dumps(asdict(should_keep_expression), indent=4))
        if matching_expression:
            print(f"matching expression: {matching_expression}")
        print(f"should_keep() result: {result}; test pass/fail below")
        print("\n")
    assert bool(result) == should_keep_expression.keep_expected


@pytest.mark.parametrize('should_id_expression', [expression for expression in expressions_test_list() if expression.id_expected is not None])
def test_should_id(should_id_expression: ExpressionTest, mocker):
    mocker.patch.object(bnip_actions, 'bnip_expressions', [
        generate_expression_object(should_id_expression.expression)
    ])
    result = bnip_actions.should_id(should_id_expression.read_json)
    if bool(result) != should_id_expression.id_expected:
        print("\n")
        print("bnip_expressions object:")
        print(pretty_dict(asdict(bnip_actions.bnip_expressions[0])))
        print("test expression object:")
        print(json.dumps(asdict(should_id_expression), indent=4))
        print(f"should_id() result: {result}; test pass/fail below")
        print("\n")
    assert bool(result) == should_id_expression.id_expected