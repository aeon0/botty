from tesserocr import PyTessBaseAPI, PSM, OEM
import numpy as np
import cv2
import re

from typing import List, Union
from dataclasses import dataclass

@dataclass
class OcrResult:
    text: str = None
    word_confidences: list = None
    mean_confidence: float = None
    original_img: np.ndarray = None
    processed_img: np.ndarray = None
    def __getitem__(self, key):
        return super().__getattribute__(key)

class Ocr:
    def __init__(self):
        self.I_regex = re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9])")
        self.One_regex = re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]")

    def prep_input_img(self, image: np.ndarray = None, clean: bool = False) -> np.ndarray:
        if clean:
            # Cleanup image with erosion image as marker with morphological reconstruction
            image = image[:, :, :]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 14, 255, cv2.THRESH_BINARY)[1]
            kernel = np.ones((3, 3), np.uint8)
            marker = thresh.copy()
            marker[1:-1, 1:-1] = 0
            while True:
                tmp = marker.copy()
                marker = cv2.dilate(marker, kernel)
                marker = cv2.min(thresh, marker)
                difference = cv2.subtract(marker, tmp)
                if cv2.countNonZero(difference) <= 0:
                    break
            mask_r = cv2.bitwise_not(marker)
            mask_color_r = cv2.cvtColor(mask_r, cv2.COLOR_GRAY2BGR)
            image = cv2.bitwise_and(image, mask_color_r)
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

    def fix_ocr_output(self, ocr_output: str) -> str:
        # case: a 1 within a string; e.g., "W1RT'S LEG"
        # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
        ocr_output = self.I_regex.sub('1', ocr_output)
        ocr_output = self.One_regex.sub('I', ocr_output)

        # case: a solitary I; e.g., " I TO 5 DEFENSE"
        while True:
            if " I " in ocr_output:
                ocr_output = ocr_output.replace(" I ", " 1 ")
                continue
            break
        # case: consecutive I's; e.g., "DEFENSE: II"
        repeat=False
        while "II" in ocr_output:
            ocr_output = ocr_output.replace("II", "11")
            repeat=True
        if repeat:
            self.fix_ocr_output(ocr_output)

        # # manual edits...:
        # ocr_output.replace("SHIFLD", "SHIELD")
        # ocr_output.replace("SPFAR", "SPEAR")
        # ocr_output.replace("GLOVFS", "GLOVES")
        # ocr_output.replace("TELEFORT", "TELEPORT")
        # ocr_output.replace("TROPHV", "TROPHY")
        # ocr_output.replace("CLAVMORE", "CLAYMORE")
        # ocr_output.replace("MAKIMUM", "MAXIMUM")

        return ocr_output

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

    def images_to_text(self, images: Union[np.ndarray, List[np.ndarray]], ocr_language: str = "engd2r_inv_th", multiline: bool = False) -> list[str]:
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
            for image in images:
                if multiline:
                    processed_img = self.prep_input_img(image)
                else:
                    processed_img = self.prep_input_img(image, clean = True)
                api.SetImageBytes(*self.img_to_bytes(processed_img))
                text = api.GetUTF8Text()
                if not multiline:
                    text = text.replace('\n', '')
                # TODO: delete words with very low confidence
                results.append(OcrResult(
                    text = self.fix_ocr_output(text),
                    word_confidences = api.AllWordConfidences(),
                    mean_confidence = api.MeanTextConf(),
                    original_img = image,
                    processed_img = processed_img
                ))
        return results