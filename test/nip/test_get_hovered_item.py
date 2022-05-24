import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem
from functools import cache
from keep_item_test_cases import NIP_TESTS
from nip.transpile import _test_nip_expression, transpile_nip_expression
import screen
from dataclasses import dataclass


PATH='test/assets/hovered_items'
screen.set_window_position(0, 0)

@dataclass
class ExpressionTest():
    basename: str = None
    expression: str = None
    transpiled: str = None
    read_json: dict = None
    expected_result: bool = False

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
    for key, value in NIP_TESTS.items():
        for val in value:
            expressions.append(ExpressionTest(
                basename=key,
                read_json=load_hovered_items()[key].as_dict(),
                expression=val[0],
                expected_result=val[1],
                transpiled=transpile_nip_expression(val[0])
            ))
    return expressions

@pytest.mark.parametrize('hovered_item', load_hovered_items().items())
def test_hovered_item(hovered_item: list[str, dict]):
    basename = hovered_item[0]
    result = hovered_item[1]
    expected_properties = HoveredItem.from_json(open(f"{PATH}/{basename}.json").read())
    assert result == expected_properties

@pytest.mark.parametrize('expression_test', expressions_test_list())
def test_keep_item(expression_test: ExpressionTest):
    print(f"\nImage: {expression_test.basename}")
    print(f"Read item: {expression_test.read_json}")
    print(f"Expression: {expression_test.expression}")
    print(f"Transpiled: {expression_test.transpiled}")
    print(f"Expected result: {expression_test.expected_result}\n")
    assert _test_nip_expression(expression_test.read_json, expression_test.expression) == expression_test.expected_result
