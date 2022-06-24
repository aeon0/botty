import pytest

from bnip.BNipExceptions import BNipSyntaxError
from bnip.transpile import generate_expression_object, transpile_bnip_expression
from transpile_test_cases import GENERAL_SYNTAX_TESTS, SYNTAX_ERROR_TESTS


def test_general_syntax():
    for general_syntax_test in GENERAL_SYNTAX_TESTS:
        try:
            transpile_bnip_expression(general_syntax_test["raw_expression"])
            if general_syntax_test["should_fail"]:
                pytest.fail(f"Syntax test failed to fail: {general_syntax_test['raw_expression']}")
        except BNipSyntaxError:
            if general_syntax_test["should_fail"]:
                continue
            else:
                pytest.fail(f"Syntax error should not have been raised for {general_syntax_test['raw_expression']}")


@pytest.mark.parametrize('syntax_test', SYNTAX_ERROR_TESTS)
def test_syntax_errors(syntax_test: dict):
    try:
        generate_expression_object(syntax_test["raw_expression"])
        assert True == False # should always fail
    except Exception as e:
        if isinstance(e, BNipSyntaxError):
            assert e.error_code == f"BNIP_{syntax_test['expected_code']}"