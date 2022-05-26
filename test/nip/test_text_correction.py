import pytest
from d2r_image import ocr, processing_helpers, d2data_lookup


@pytest.mark.parametrize("ocr_string, expected_string", [
    ("SUPERIER ZWEIHANDRE", 'SUPERIOR ZWEIHANDER'),
    ("PARFECT RUBV", 'PERFECT RUBY'),
    ("SUPERIOR QU AB", 'SUPERIOR QUHAB')
])
def test_wordwise_check(ocr_string, expected_string):
    confidences = [0.5 for x in ocr_string.split()]
    result = ocr._ocr_result_dictionary_check(ocr_string, confidences)
    assert result == expected_string

@pytest.mark.parametrize("ocr_string, expected", [
    ("JAR RUNE", (None, 'JAH RUNE')),
    ("LOW QUALITY RUNE BONG", ("LOW QUALITY", 'RUNE BOW')),
    ("SUPERIOR CHAMPION WORD", ("SUPERIOR", 'CHAMPION SWORD'))
])
def test_base_item_check(ocr_string, expected):
    quality, normalized_text = processing_helpers.get_normalized_normal_gray_item_text(ocr_string)
    base_item = f"{processing_helpers.fuzzy_base_item_match(normalized_text)}".strip()
    quality = quality.value if quality else None
    assert (quality, base_item) == expected