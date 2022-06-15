import pytest

from nip.lexer import NipSyntaxError
from nip.transpile import transpile_nip_expression
from transpile_test_cases import general_syntax_tests


def test_general_syntax():
    for general_syntax_test in general_syntax_tests:
        try:
            transpile_nip_expression(general_syntax_test["raw_expression"])
            if general_syntax_test["should_fail"]:
                pytest.fail(f"Syntax test failed to fail: {general_syntax_test['raw_expression']}")
        except NipSyntaxError:
            if general_syntax_test["should_fail"]:
                continue
            else:
                pytest.fail(f"Syntax error should not have been raised for {general_syntax_test['raw_expression']}")