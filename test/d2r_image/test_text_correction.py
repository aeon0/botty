import pytest
from d2r_image import ocr


@pytest.mark.parametrize("ocr_string, expected_string", [
    ("SUPERIER ZWEIHANDRE", 'SUPERIOR ZWEIHANDER'),
    ("PARFECT RUBV", 'PERFECT RUBY'),
    ("SUPERIOR QU AB", 'SUPERIOR QUHAB')
])
def test_wordwise_check(ocr_string, expected_string):
    confidences = [0.5 for x in ocr_string.split(" ")]
    result = ocr._ocr_result_dictionary_check(ocr_string, confidences)
    assert result == expected_string