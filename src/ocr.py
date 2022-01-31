from fileinput import close
from tesserocr import PyTessBaseAPI, PSM, OEM
import numpy as np
import cv2
import re
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
    original_img: np.ndarray = None
    processed_img: np.ndarray = None
    def __getitem__(self, key):
        return super().__getattribute__(key)

class Ocr:
    def __init__(self):
        self.I_1 = re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9\-+])")
        self.II_U = re.compile(r"(?<=[A-Z])II|II(?=[A-Z])|1?=[a-z]")
        self.One_I = re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]")
        self.OneOne_U = re.compile(r"(?<=[A-Z])11|11(?=[A-Z])|1?=[a-z]")
        with open('assets/tessdata/d2r.user-words') as file:
            self.word_list = [line.rstrip() for line in file]

    def check_wordlist(self, text: str = None, confidences: list = []) -> str:
        word_count=0
        new_string=""
        text = text.replace('\n',' NEWLINEHERE ')
        for word in text.split(' '):
            word = word.strip()
            if word and word != "NEWLINEHERE":
                try:
                    if confidences[word_count] <= 88:
                        if (word not in self.word_list) and (re.sub(r"[^a-zA-Z0-9]", "", word) not in self.word_list):
                            closest_match = difflib.get_close_matches(word, self.word_list, cutoff=0.9)
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

    def prep_inv_th(self, image: np.ndarray = None, clean: bool = False) -> np.ndarray:
        if clean:
            image = erode_to_black(image)
        # crop
        image = image[4: image.shape[0]-4, 5: image.shape[1]-5]
        # re-pad
        image = np.pad(image, pad_width=[(4, 4),(4, 4),(0, 0)], mode='constant')
        # threshold
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.threshold(image, 25, 255, cv2.THRESH_BINARY)[1]
        # invert
        image = cv2.bitwise_not(image)
        return image

    def fix_ocr_output(self, ocr_output: str, repeat_count: int = 0) -> str:
        # case: two 1's within a string; e.g., "SIIPER MANA POTION"
        try:
            text = self.II_U.sub('U', ocr_output)
        except:
            Logger.error(f"Error _II_ -> _U_ on {ocr_output}")
            text = ocr_output
        # case: two 1's within a string; e.g., "S11PER MANA POTION"
        try:
            text = self.OneOne_U.sub('U', text)
        except:
            Logger.error(f"Error _11_ -> _U_ on {ocr_output}")
        # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
        try:
            text = self.I_1.sub('1', text)
        except:
            Logger.error(f"Error I -> 1 on {ocr_output}")
        # case: a 1 within a string; e.g., "W1RT'S LEG"
        try:
            text = self.One_I.sub('I', text)
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
            self.fix_ocr_output(text)

        # manual edits...:
        text = text.replace("SHIFLD", "SHIELD")
        text = text.replace("SPFAR", "SPEAR")
        text = text.replace("GLOVFS", "GLOVES")
        text = text.replace("TELEFORT", "TELEPORT")
        text = text.replace("TROPHV", "TROPHY")
        text = text.replace("CLAVMORE", "CLAYMORE")
        text = text.replace("MAKIMUM", "MAXIMUM")
        text = text.replace("DEKTERITY", "DEXTERITY")
        text = text.replace("DERTERITY", "DEXTERITY")
        text = text.replace("QUAHTITY", "QUANTITY")
        text = text.replace("DEFERSE", "DEFENSE")
        text = text.replace("ARMGR", "ARMOR")
        text = text.replace("ARMER", "ARMOR")
        text = text.replace("COMDAT", "COMBAT")
        text = text.replace("WEAPORS", "WEAPONS")
        text = text.replace("AXECLASS", "AXE CLASS")
        text = text.replace("IOX%", "10%")
        text = text.replace("IO%", "10%")
        text = text.replace("TWYO", "TWO")

        return text

    def img_to_bytes(self, image: np.ndarray, colorspace: str = 'BGR'):
        """ Sets an OpenCV-style image for recognition.
        https://github.com/sirfz/tesserocr/issues/198

        """
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

    def images_to_text(self, images: Union[np.ndarray, List[np.ndarray]], ocr_language: str = "engd2r_inv_th", multiline: bool = False, process_mode: str = "inv_th") -> list[str]:
        if type(images) == np.ndarray:
            images = [images]
        # segmentation_mode = PSM.RAW_LINE
        # AUTO is slower workaround due to poor text recognition when
        # drops are bordered by other drops horizontally but slightly staggered
        # see: https://www.pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
        segmentation_mode = PSM.AUTO
        if multiline:
            segmentation_mode = PSM.SINGLE_BLOCK
        results = []
        with PyTessBaseAPI(psm=segmentation_mode, oem=OEM.LSTM_ONLY, path=f"assets/tessdata/{ocr_language}", lang=ocr_language ) as api:
            api.ReadConfigFile("assets/tessdata/ocr_config.txt")
            api.SetSourceResolution(72)
            for image in images:
                if process_mode == "inv_th":
                    if multiline:
                        clean = False
                    else:
                        clean = True
                    processed_img = self.prep_inv_th(image, clean = clean)
                else:
                    processed_img = image
                api.SetImageBytes(*self.img_to_bytes(processed_img))
                original_text = api.GetUTF8Text()
                text = original_text
                if not multiline:
                    text = text.replace('\n', '')
                word_confidences = api.AllWordConfidences()
                text = self.fix_ocr_output(text)
                if any([x <= 88 for x in word_confidences]):
                #try:
                    text = self.check_wordlist(text, word_confidences)
                #except:
                #    Logger.error(f"check_wordlist: failed on {text}")
                results.append(OcrResult(
                    original_text = original_text,
                    text = text,
                    word_confidences = word_confidences,
                    mean_confidence = api.MeanTextConf(),
                    original_img = image,
                    processed_img = processed_img
                ))
        return results