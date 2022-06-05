import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.data_models import GroundItemList
from common import ExpressionTest
from functools import cache
from pick_item_test_cases import NIP_PICK_TESTS
import nip.transpile as nip_transpile
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
                            expected_result=expr[1],
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


@pytest.mark.parametrize('expression_test', expressions_test_list())
def test_keep_item(expression_test: ExpressionTest, mocker):
    should_pick_transpiled = nip_transpile.transpile_nip_expression(expression_test.expression.split("#")[0], isPickedUpPhase=True)
    mocker.patch.object(nip_transpile, 'nip_expressions', [
        nip_transpile.NIPExpression(
                raw=expression_test.expression,
                should_id_transpiled=nip_transpile.transpile_nip_expression(expression_test.expression.split("#")[0]),
                transpiled=expression_test.transpiled,
                should_pickup=should_pick_transpiled
            )
    ])
    result, _ = nip_transpile.should_pickup(expression_test.read_json)
    if bool(result) != expression_test.expected_result:
        print(f"\nImage: {expression_test.basename}")
        print(f"Read item: {expression_test.read_json}")
        print(f"Expression: {expression_test.expression}")
        print(f"Transpiled: {expression_test.transpiled}")
        print(f"should_pick() transpiled: {should_pick_transpiled}")
        print(f"Expected result: {expression_test.expected_result}")
        print(f"Result: {result}\n")
    assert bool(result) == expression_test.expected_result
