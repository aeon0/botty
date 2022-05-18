import pytest

from nip.lexer import NipSyntaxError
from nip.transpile import transpile_nip_expression, should_keep, should_pickup, should_id, NipSyntaxErrorSection
from transpile_test_cases import items, general_syntax_tests, transpile_tests, section_syntax_tests

# * https://docs.pytest.org/en/7.1.x/getting-started.html
# * https://docs.pytest.org/en/7.1.x/how-to/index.html
    
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
   

def test_section_syntax():
    for section_syntax_test in section_syntax_tests:
        try:
            transpile_nip_expression(section_syntax_test["raw_expression"])
            if section_syntax_test["should_fail"]:
                pytest.fail(f"Syntax test failed to fail: {section_syntax_test['raw_expression']}")
        except NipSyntaxErrorSection:
            if section_syntax_test["should_fail"]:
                continue
            else:
                pytest.fail(f"Syntax error should not have been raised for {section_syntax_test['raw_expression']}")

def test_transpile():
    for transpile_test in transpile_tests:
        assert transpile_nip_expression(transpile_test["raw_expression"]) == transpile_test["transpiled_expression"]

