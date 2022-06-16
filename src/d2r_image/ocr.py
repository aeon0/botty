from tesserocr import PyTessBaseAPI, OEM
import numpy as np
import cv2
from utils.misc import erode_to_black, find_best_match
from d2r_image.data_models import OcrResult
from d2r_image.ocr_data import ERROR_RESOLUTION_MAP, I_1, II_U, ONE_I, ONEONE_U
from d2r_image.strings_store import all_words
from logger import Logger

def image_to_text(
    images: np.ndarray | list[np.ndarray],
    model: str = "hover-eng_inconsolata_inv_th_fast",
    psm: int = 3,
    word_list: str = "assets/word_lists/all_words.txt",
    scale: float = 1.0,
    crop_pad: bool = True,
    erode: bool = False,
    invert: bool = True,
    threshold: int = 25,
    digits_only: bool = False,
    fix_regexps: bool = True,
    check_known_errors: bool = True,
    correct_words: bool = True,
) -> list[OcrResult]:
    """
    Uses Tesseract to read image(s)
    :param images (required): image or list of images to read in OpenCV format.
        Use a list of images rather than looping over single images where possible for best performance.
    :param model: OCR language model basename to use (in assets/tessdata folder)
    :param psm: Tesseract PSM to use. 7=single uniform text line, 6=single block of text, 3=auto without orientation.
        See https://www.pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
    :param word_list: predefined wordlist to use. Tesseract will use these to help with recognition
    :param scale: scales input image, sometimes necessary for smaller text (but doesn't always improve accuracy). Engd2r_inv_th trained on ~1.6x scaled assets.
    :param crop_pad: crop the outer part and then re-pad image. Intended for item drops.
    :param erode: use erosion function to erode image to black borders (i.e. for item drops)
    :param invert: invert and threshold the input image(s)
    :param threshold: apply threshold to image (ex. 25 would threshold around V=25). Set to 0 to not threshold image.
    :param digits_only: only look for digits
    :param fix_regexps: use regex for various cases of common errors (I <-> 1, etc.)
    :param check_known_errors: check for predefined common errors and replace
    :param correct_words: check dictionary of words and match closest match
    :return: Returns an OcrResult object
    """
    if type(images) == np.ndarray:
        images = [images]
    results = []

    with PyTessBaseAPI(psm=psm, oem=OEM.LSTM_ONLY, path=f"assets/tessdata", lang=model ) as api:
        api.ReadConfigFile("assets/tessdata/ocr_config.txt")
        if word_list:
            api.SetVariable("user_words_file", word_list)
        #api.SetSourceResolution(72 * scale)
        for image in images:
            processed_img = image
            if scale:
                processed_img = cv2.resize(
                    processed_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            if erode:
                processed_img = erode_to_black(processed_img)
            if crop_pad:
                processed_img = _crop_pad(processed_img)
            image_is_binary = (image.shape[2] if len(
                image.shape) == 3 else 1) == 1 and image.dtype == bool
            if not image_is_binary and threshold:
                processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
                processed_img = cv2.threshold(
                    processed_img, threshold, 255, cv2.THRESH_BINARY)[1]
            if invert:
                if threshold or image_is_binary:
                    processed_img = cv2.bitwise_not(processed_img)
                else:
                    processed_img = ~processed_img
            api.SetImageBytes(*_img_to_bytes(processed_img))
            if digits_only:
                api.SetVariable("tessedit_char_blacklist",
                                ".,!?@#$%&*()<>_-+=/:;'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
                api.SetVariable("tessedit_char_whitelist", "0123456789")
                api.SetVariable("classify_bln_numeric_mode", "1")
            original_text = api.GetUTF8Text()
            text = original_text
            # replace newlines if image is a single line
            if psm in (7, 8, 13):
                text = text.replace('\n', '')
            word_confidences = api.AllWordConfidences()
            if fix_regexps:
                text = _fix_regexps(text)
            if check_known_errors:
                text = _check_known_errors(text)
            if correct_words:
                text = _ocr_result_dictionary_check(text, word_confidences)
            results.append(OcrResult(
                original_text=original_text,
                text=text,
                #processed_img=processed_img,
                word_confidences=word_confidences,
                mean_confidence=api.MeanTextConf()
            ))
        return results


def _crop_pad(image: np.ndarray = None):
    # crop
    image = image[4: image.shape[0]-4, 5: image.shape[1]-5]
    # re-pad
    image = np.pad(image, pad_width=[(4, 4), (4, 4), (0, 0)], mode='constant')
    return image


def _img_to_bytes(image: np.ndarray, colorspace: str = 'BGR'):
    # Sets an OpenCV-style image for recognition: https://github.com/sirfz/tesserocr/issues/198
    bytes_per_pixel = image.shape[2] if len(image.shape) == 3 else 1
    height, width = image.shape[:2]
    bytes_per_line = bytes_per_pixel * width
    if bytes_per_pixel != 1 and colorspace != 'RGB':
        # non-RGB color image -> convert to RGB
        image = cv2.cvtColor(image, getattr(cv2, f'COLOR_{colorspace}2RGB'))
    elif bytes_per_pixel == 1 and image.dtype == bool:
        # binary image -> convert to bitstream
        image = np.packbits(image, axis=1)
        bytes_per_line = image.shape[1]
        width = bytes_per_line * 8
        bytes_per_pixel = 0
    # else image already RGB or grayscale
    return image.tobytes(), width, height, bytes_per_pixel, bytes_per_line


def _fix_regexps(ocr_output: str, repeat_count: int = 0) -> str:
    # case: two 1's within a string; e.g., "SIIPER MANA POTION"
    try:
        text = II_U.sub('U', ocr_output)
    except:
        # logging.error(f"Error _II_ -> _U_ on {ocr_output}")
        text = ocr_output
    # case: two 1's within a string; e.g., "S11PER MANA POTION"
    try:
        text = ONEONE_U.sub('U', text)
    except:
        # logging.error(f"Error _11_ -> _U_ on {ocr_output}")
        pass
    # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
    try:
        text = I_1.sub('1', text)
    except:
        # logging.error(f"Error I -> 1 on {ocr_output}")
        pass
    # case: a 1 within a string; e.g., "W1RT'S LEG"
    try:
        text = ONE_I.sub('I', text)
    except:
        # logging.error(f"Error 1 -> I on {ocr_output}")
        pass
    # case: a solitary I; e.g., " I TO 5 DEFENSE"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error ' I ' -> ' 1 ' on {ocr_output}")
            break
        if " I " in text:
            text = text.replace(" I ", " 1 ")
            continue
        elif ' I\n' in text:
            text = text.replace(' I\n', ' 1\n')
            continue
        elif '\nI ' in text:
            text = text.replace('\nI ', '\n1 ')
            continue
        break
    # case: a solitary S; e.g., " 1 TO S DEFENSE"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error ' S ' -> ' 5 ' on {ocr_output}")
            break
        if " S " in text:
            text = text.replace(" S ", " 5 ")
            continue
        elif ' I\n' in text:
            text = text.replace(' S\n', ' 5\n')
            continue
        elif '\nI ' in text:
            text = text.replace('\nS ', '\n5 ')
            continue
        break
    # case: a solitary O; e.g., " O TO 5 DEFENSE"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error ' I ' -> ' 1 ' on {ocr_output}")
            break
        if (pattern := " O ") in text:
            text = text.replace(pattern, " 0 ")
            continue
        elif (pattern := ' O\n') in text:
            text = text.replace(pattern, ' 0\n')
            continue
        elif (pattern := '\nO ') in text:
            text = text.replace(pattern, '\n0 ')
            continue
        break
    # case: consecutive I's; e.g., "DEFENSE: II"
    repeat = False
    cnt = 0
    while "II" in text:
        cnt += 1
        if cnt > 30:
            # logging.error(f"Error 4 on {ocr_output}")
            break
        text = text.replace("II", "11")
        repeat = True
        repeat_count += 1
    if repeat and repeat_count < 10:
        _fix_regexps(text)
    return text


def _check_known_errors(text):
    for word in text.split():
        for key in ERROR_RESOLUTION_MAP:
            if key == word:
                text = text.replace(key, ERROR_RESOLUTION_MAP[key])
                Logger.debug(f"_check_known_errors: {key} -> {ERROR_RESOLUTION_MAP[key]}")
    return text

def _contains_characters(word):
    return any(c.isalpha() for c in word)

def _ocr_result_dictionary_check(
    original_text: str,
    confidences: list,
    word_list: set = all_words(),
    normalized_lev_threshold: float = 0.6
    ) -> str:
    confidences = [x/100 for x in confidences]
    words_by_lines = [line.strip().split() for line in original_text.splitlines()]
    total_word_count = -1
    new_text = ""
    saved_result = ""
    skip_next = False
    for line_cnt, line in enumerate(words_by_lines):
        new_line = []
        for word_cnt, word in enumerate(line):
            total_word_count += 1 # increment before skip check to maintain relationship with confidences
            # if the word was incorporated in the previous word as a combined substitution, skip
            if skip_next:
                skip_next = False
                continue
            # if word exists in list or is non-alphabetical, keep
            if word in word_list or not _contains_characters(word):
                new_line.append(word)
                continue
            # if the word is bounded by single quotes, then it's likely a runeword e.g. 'taltireth'
            if word.startswith("'") and word.endswith("'") and len(word) > 1:
                new_line.append(word)
                continue
            # fuzzy match the word
            # if the word has already been calculated on a lookahead check, used stored result
            if saved_result:
                result = saved_result
                saved_result = ""
            else:
                result = find_best_match(word, list(word_list))
            # if the word is the last word on the line don't lookahead
            if word_cnt == (len(line) - 1):
                if result.score_normalized >= normalized_lev_threshold:
                    # Logger.debug(f"_ocr_result_dictionary_check: change {word} -> {result.match} similarity: {result.score_normalized*100:.1f}%, OCR confidence: {int(confidences[total_word_count]*100)}%")
                    new_line.append(result.match)
                else:
                    new_line.append(word)
                continue
            # if the word is not the last word, try lookahead in case of misread character -> space
            next_word = line[word_cnt + 1]
            # if next word is in wordlist or doesn't contain characters, save current word
            if next_word in word_list or not _contains_characters(word):
                if result.score_normalized >= normalized_lev_threshold:
                    # Logger.debug(f"_ocr_result_dictionary_check: change {word} -> {result.match} similarity: {result.score_normalized*100:.1f}%, OCR confidence: {int(confidences[total_word_count]*100)}%")
                    new_line.append(result.match)
                else:
                    new_line.append(word)
                continue
            # fuzzy match the next word and a combination of both current and next words
            next_result = find_best_match(next_word, list(word_list))
            combined_result = find_best_match(f"{word} {next_word}", list(word_list))
            if combined_result.score < (result.score + next_result.score):
                # combined lev score is superior to sum of individual lev scores, replace with combined string
                skip_next = True
                # Logger.debug(f'_ocr_result_dictionary_check: change "{word} {next_word}" -> {combined_result.match} similarity: {combined_result.score_normalized*100:.1f}%, OCR confidence: {int(confidences[total_word_count]*100)}%, {int(confidences[total_word_count+1]*100)}%')
                new_line.append(combined_result.match)
            else:
                if result.score_normalized >= normalized_lev_threshold:
                    # Logger.debug(f"_ocr_result_dictionary_check: change {word} -> {result.match} similarity: {result.score_normalized*100:.1f}%, OCR confidence: {int(confidences[total_word_count]*100)}%")
                    new_line.append(result.match)
                else:
                    new_line.append(word)
                # save next_result for next iteration
                saved_result = next_result
        new_text += f"{' '.join(new_line)}"
        if line_cnt < (len(words_by_lines) - 1):
            new_text += "\n"
    return new_text