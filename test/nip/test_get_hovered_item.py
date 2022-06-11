import os
import cv2
import json
from dataclasses import asdict
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem
from functools import cache
from keep_item_test_cases import NIP_KEEP_TESTS
from common import ExpressionTest
import screen
import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called
import nip.transpile as nip_transpile
from nip.actions import should_id, should_keep


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
    for key, value in NIP_KEEP_TESTS.items():
        for val in value:
            expressions.append(ExpressionTest(
                basename=key,
                read_json=load_hovered_items()[key].as_dict(),
                expression=val["expression"],
                keep_or_pick_expected=val["should_keep"],
                id_expected=None if not "should_id" in val else val["should_id"],
                transpiled=nip_transpile.transpile_nip_expression(val["expression"])
            ))
    return expressions

@pytest.mark.parametrize('hovered_item', load_hovered_items().items())
def test_hovered_item(hovered_item: list[str, dict]):
    basename = hovered_item[0]
    result = hovered_item[1]
    expected_properties = HoveredItem.from_json(open(f"{PATH}/{basename}.json").read())
    assert result == expected_properties

@pytest.mark.parametrize('should_keep_expression', expressions_test_list())
def test_keep_item(should_keep_expression: ExpressionTest, mocker):
    mocker.patch.object(nip_transpile, 'nip_expressions', [
        nip_transpile.load_nip_expression(should_keep_expression.expression)
    ])
    result, _ = should_keep(should_keep_expression.read_json)
    if bool(result) != should_keep_expression.keep_or_pick_expected:
        print("\n")
        print(json.dumps(asdict(should_keep_expression), indent=4))
        print(f"should_keep result: {result}; test pass/fail below")
        print("\n")
    assert bool(result) == should_keep_expression.keep_or_pick_expected


@pytest.mark.parametrize('should_id_expression', expressions_test_list())
def test_should_id(should_id_expression: ExpressionTest, mocker):
    if should_id_expression.id_expected is not None:
        mocker.patch.object(nip_transpile, 'nip_expressions', [
            nip_transpile.load_nip_expression(should_id_expression.expression)
        ])
        result = should_id(should_id_expression.read_json)
        if bool(result) != should_id_expression.id_expected:
            print("\n")
            print(json.dumps(asdict(should_id_expression), indent=4))
            print(f"should_id result: {result}; test pass/fail below")
        assert bool(result) == should_id_expression.id_expected