from fileinput import close
from tesserocr import PyTessBaseAPI, PSM, OEM
import numpy as np
import cv2
import re
import csv
import difflib
from utils.misc import erode_to_black

from logger import Logger
from typing import List, Union
from dataclasses import dataclass

@dataclass
class OcrResult:
    text: str = None
    original_text: str = None
    word_confidences: list = None
    mean_confidence: float = None
    # these are kept to help train OCR
    original_img: np.ndarray = None
    processed_img: np.ndarray = None
    def __getitem__(self, key):
        return super().__getattribute__(key)

class Ocr:
    def __init__(self):
        self._I_1 = re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9\-+])")
        self._II_U = re.compile(r"(?<=[A-Z])II|II(?=[A-Z])|1?=[a-z]")
        self._One_I = re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]")
        self._OneOne_U = re.compile(r"(?<=[A-Z])11|11(?=[A-Z])|1?=[a-z]")
        with open('assets/tessdata/ocr_errors.csv') as file:
            self._ocr_errors = dict(csv.reader(file, skipinitialspace = False, delimiter = ',', quoting = csv.QUOTE_NONE))

    """
    OCR input processing functions:
    """
    def _crop_pad(self, image: np.ndarray = None):
        # crop
        image = image[4: image.shape[0]-4, 5: image.shape[1]-5]
        # re-pad
        image = np.pad(image, pad_width=[(4, 4),(4, 4),(0, 0)], mode='constant')
        return image

    """
    OCR functions:
    """

    def _img_to_bytes(self, image: np.ndarray, colorspace: str = 'BGR'):
        # Sets an OpenCV-style image for recognition: https://github.com/sirfz/tesserocr/issues/198
        bytes_per_pixel = image.shape[2] if len(image.shape) == 3 else 1
        height, width   = image.shape[:2]
        bytes_per_line  = bytes_per_pixel * width

        if bytes_per_pixel != 1 and colorspace != 'RGB':
            # non-RGB color image -> convert to RGB
            image = cv2.cvtColor(image, getattr(cv2, f'COLOR_{colorspace}2RGB'))
        elif bytes_per_pixel == 1 and image.dtype == bool:
            # binary image -> convert to bitstream
            image = np.packbits(image, axis=1)
            bytes_per_line  = image.shape[1]
            width = bytes_per_line * 8
            bytes_per_pixel = 0
        # else image already RGB or grayscale

        return image.tobytes(), width, height, bytes_per_pixel, bytes_per_line

    def image_to_text(self,
        images: Union[np.ndarray, List[np.ndarray]],
        model: str = "engd2r_inv_th",
        psm: int = 3,
        word_list: str = "all_strings.txt",
        scale: float = 1.0,
        crop_pad: bool = True,
        erode: bool = True,
        invert: bool = True,
        threshold: int = 25,
        digits_only: bool = False,
        fix_regexps: bool = True,
        check_known_errors: bool = True,
        check_wordlist: bool = True,
        word_match_threshold: float = 0.9
    ) -> list[str]:
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
        :param check_wordlist: check dictionary of words and match closest match if proximity is greater than word_match_threshold
        :param word_match_threshold: (see check_wordlist)
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
                    processed_img = cv2.resize(processed_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
                if crop_pad:
                    processed_img = self._crop_pad(processed_img)
                if erode:
                    processed_img = erode_to_black(processed_img)
                image_is_binary = (image.shape[2] if len(image.shape) == 3 else 1) == 1 and image.dtype == bool
                if image_is_binary:
                    if threshold:
                        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
                        processed_img = cv2.threshold(processed_img, threshold, 255, cv2.THRESH_BINARY)[1]
                if invert:
                    if threshold or image_is_binary:
                        processed_img = cv2.bitwise_not(processed_img)
                    else:
                        processed_img = ~processed_img
                api.SetImageBytes(*self._img_to_bytes(processed_img))
                if digits_only:
                    api.SetVariable("tessedit_char_blacklist", ".,!?@#$%&*()<>_-+=/:;'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
                    api.SetVariable("tessedit_char_whitelist", "0123456789")
                original_text = api.GetUTF8Text()
                text = original_text
                # replace newlines if image is a single line
                if psm in (7, 8, 13):
                    text = text.replace('\n', '')
                word_confidences = api.AllWordConfidences()
                if fix_regexps:
                    text = self._fix_regexps(text)
                if check_known_errors:
                    text = self._check_known_errors(text)
                if check_wordlist and any([x <= 88 for x in word_confidences]):
                    text = self._check_wordlist(text, word_list, word_confidences, word_match_threshold)
                results.append(OcrResult(
                    original_text = original_text,
                    text = text,
                    word_confidences = word_confidences,
                    mean_confidence = api.MeanTextConf(),
                    original_img = image,
                    processed_img = processed_img
                ))
        return results

    """
    OCR output processing functions:
    """
    def _check_known_errors(self, text):
        for key, value in self._ocr_errors.items():
            if key in text:
                text = text.replace(key, value)
        return text

    def _check_wordlist(self, text: str = None, word_list: str = None, confidences: list = [], match_threshold: float = 0.9) -> str:
        with open(f'assets/tessdata/word_lists/{word_list}') as file:
            word_list = [line.rstrip() for line in file]

        word_count=0
        new_string=""
        text = text.replace('\n',' NEWLINEHERE ')
        for word in text.split(' '):
            word = word.strip()
            if word and word != "NEWLINEHERE":
                try:
                    if confidences[word_count] <= 88:
                        if (word not in word_list) and (re.sub(r"[^a-zA-Z0-9]", "", word) not in word_list):
                            closest_match = difflib.get_close_matches(word, word_list, cutoff=match_threshold)
                            if closest_match and closest_match != word:
                                new_string += f"{closest_match[0]} "
                                Logger.debug(f"check_wordlist: Replacing {word} ({confidences[word_count]}%) with {closest_match[0]}, score=")
                            else:
                                new_string += f"{word} "
                        else:
                            new_string += f"{word} "
                    else:
                        new_string += f"{word} "
                    word_count += 1
                except IndexError:
                    # bizarre word_count index exceeded sometimes... can't reproduce and words otherwise seem to match up
                    Logger.error(f"check_wordlist: IndexError for word: {word}, index: {word_count}, text: {text}")
                    return text
                except:
                    Logger.error(f"check_wordlist: Unknown error for word: {word}, index: {word_count}, text: {text}")
                    return text
            elif word == "NEWLINEHERE":
                new_string += "\n"
        return new_string.strip()

    def _fix_regexps(self, ocr_output: str, repeat_count: int = 0) -> str:
        # case: two 1's within a string; e.g., "SIIPER MANA POTION"
        try:
            text = self._II_U.sub('U', ocr_output)
        except:
            Logger.error(f"Error _II_ -> _U_ on {ocr_output}")
            text = ocr_output
        # case: two 1's within a string; e.g., "S11PER MANA POTION"
        try:
            text = self._OneOne_U.sub('U', text)
        except:
            Logger.error(f"Error _11_ -> _U_ on {ocr_output}")
        # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
        try:
            text = self._I_1.sub('1', text)
        except:
            Logger.error(f"Error I -> 1 on {ocr_output}")
        # case: a 1 within a string; e.g., "W1RT'S LEG"
        try:
            text = self._One_I.sub('I', text)
        except:
            Logger.error(f"Error 1 -> I on {ocr_output}")

        # case: a solitary I; e.g., " I TO 5 DEFENSE"
        cnt=0
        while True:
            cnt += 1
            if cnt >30:
                Logger.error(f"Error ' I ' -> ' 1 ' on {ocr_output}")
                break
            if " I " in text:
                text = text.replace(" I ", " 1 ")
                continue
            elif ' I\n'  in text:
                text = text.replace(' I\n', ' 1\n')
                continue
            elif '\nI '  in text:
                text = text.replace('\nI ', '\n1 ')
                continue
            break

        # case: consecutive I's; e.g., "DEFENSE: II"
        repeat=False
        cnt=0
        while "II" in text:
            cnt += 1
            if cnt >30:
                Logger.error(f"Error 4 on {ocr_output}")
                break
            text = text.replace("II", "11")
            repeat=True
            repeat_count += 1
        if repeat and repeat_count < 10:
            self._fix_regexps(text)

        return text

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from utils.misc import cut_roi
    from config import Config

    from screen import Screen
    screen = Screen()
    ocr = Ocr()
    img = screen.grab()
    # img = cut_roi(img, Config.ui_roi["char_selection_top"])

    Logger.debug("OCR result:")
    ocr_result = ocr.image_to_text(
        images = img,
        model = "engd2r_ui",
        psm = 3,
        word_list = "all_strings.txt",
        scale = 1.0,
        crop_pad = False,
        erode = False,
        invert = False,
        threshold = 0,
        digits_only = False,
        fix_regexps = False,
        check_known_errors = False,
        check_wordlist = False,
        word_match_threshold = 0.9
    )[0]
    Logger.debug(ocr_result.text)