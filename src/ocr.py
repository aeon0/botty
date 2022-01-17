from tesserocr import PyTessBaseAPI, PSM, OEM
import numpy as np
import cv2
import re
import time
from typing import List, Union
from utils.misc import color_filter
from logger import Logger

class Ocr:
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
        # output = re.sub(r"1(?![\s%])(?=\w+)", "I", output)
        # output = re.sub(r"(?<=\w)(?<![\s+\-])1", "I", output)
        # output = re.sub(r"I(?!\s)(?=[\d%-])", "1", output)
        # output = re.sub(r"(?<=[+\-\d])(?<!\s)I", "1", output)

        # case: an I within a number or by a sign; e.g., "+32I to mana attack rating"
        while True:
            x = re.search("[\d+-]I", ocr_output)
            if x:
                ocr_output = ocr_output[:x.start()+1] + '1' + ocr_output[x.start() + 2:]
            else:
                break
        while True:
            x = re.search("I[\d%-]", ocr_output)
            if x:
                ocr_output = ocr_output[:x.start()] + '1' + ocr_output[x.start() + 1:]
            else:
                break

        # case: a 1 within a string; e.g., "W1RT'S LEG"
        while True:
            x = re.search("[A-Z]1", ocr_output)
            if x:
                ocr_output = ocr_output[:x.start()+1] + 'I' + ocr_output[x.start() + 2:]
            else:
                break
        while True:
            x = re.search("1[A-Z]", ocr_output)
            if x:
                ocr_output = ocr_output[:x.start()] + 'I' + ocr_output[x.start() + 1:]
            else:
                break

        # case: a solitary I; e.g., " I TO 5 DEFENSE"
        while True:
            if " I " in ocr_output:
                ocr_output.replace(" I ", " 1 ")
                continue
            break

        # case: consecutive I's; e.g., "DEFENSE: II"
        repeat=False
        while "II" in ocr_output:
            ocr_output.replace("II", "11")
            repeat=True

        if repeat:
            self.fix_ocr_output(ocr_output)

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

    def images_to_text(self, images: Union[np.ndarray, List[np.ndarray]], use_language: str = "engd2r_inv_th", multiline: bool = False) -> list[str]:
        #https://www.pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
        if type(images) == np.ndarray:
            images = [images]
        if multiline:
            segmentation_mode = PSM.SINGLE_BLOCK
        else:
            # segmentation_mode = PSM.RAW_LINE
            segmentation_mode = PSM.AUTO
        results = []
        with PyTessBaseAPI(psm=segmentation_mode, oem=OEM.LSTM_ONLY, path=f"assets/tessdata/{use_language}", lang=use_language ) as api:
            #api.SetVariable('user_words_file', f"assets/tessdata/{use_language}/{use_language}.wordlist")
            api.ReadConfigFile("assets/tessdata/ocr_config.txt")
            for cnt, o_img in enumerate(images):
                if multiline:
                    image = self.prep_input_img(o_img)
                else:
                    image = self.prep_input_img(o_img, clean = True)
                api.SetImageBytes(*self.img_to_bytes(image))
                text = api.GetUTF8Text()
                if not multiline:
                    text = text.replace('\n', '')
                text = self.fix_ocr_output(text)
                confidences = api.AllWordConfidences()
                timestamp = str(round(time.time_ns() // 1_000_000 ))
                filename = "./loot_screenshots/ocr_" + timestamp + "_" + str(cnt) + "_o.png"
                cv2.imwrite(filename, o_img)
                filename = "./loot_screenshots/ocr_" + timestamp + "_" + str(cnt) + "_n.png"
                cv2.imwrite(filename, image)
                Logger.debug(f"{filename}, {text}, {confidences}")
                results.append(text)
        return results