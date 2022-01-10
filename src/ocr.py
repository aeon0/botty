from tesserocr import PyTessBaseAPI, PSM, OEM
import numpy as np
import cv2
import re
from typing import List, Union


class Ocr:
    def fix_ocr_output(self, itemtext: str) -> str:
        output = itemtext
        output = re.sub(r"1(?![\s%])(?=\w+)", "I", output)
        output = re.sub(r"(?<=\w)(?<![\s+\-])1", "I", output)
        output = re.sub(r"I(?!\s)(?=[\d%])", "1", output)
        output = re.sub(r"(?<=[+\-\d])(?<!\s)I", "1", output)
        return output

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

    def images_to_text(self, images: Union[np.ndarray, List[np.ndarray]], use_language: str = "engd2r", multiline: bool = False) -> list[str]:
        #https://www.pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
        if type(images) == np.ndarray:
            images = [images]
        if multiline:
            segmentation_mode = PSM.SINGLE_BLOCK
        else:
            segmentation_mode = PSM.RAW_LINE
        results = []
        with PyTessBaseAPI(psm=segmentation_mode, oem=OEM.LSTM_ONLY, path='assets/tessdata', lang=use_language) as api:
            for image in images:
                api.SetImageBytes(*self.img_to_bytes(image))
                if multiline:
                    text = api.GetUTF8Text()
                else:
                    text = api.GetUTF8Text().replace('\n', '')
                results.append(self.fix_ocr_output(text))
        return results