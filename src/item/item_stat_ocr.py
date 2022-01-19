import os
import cv2
import numpy as np
from typing import Dict
from collections import OrderedDict

from utils.misc import list_files_in_folder
from utils.misc import load_template, list_files_in_folder, alpha_to_mask


class LetterSequencesOCR:
    """
    A single-line reader from an image-based letters
    """

    def __init__(self, dictionary: Dict[str, np.ndarray]):
        """
        :param dictionary: the keys are the letters, the values are the image patterns.
        """
        self.dictionary = dictionary
        self.letter_sizes = {}
        self.line_height = 0
        for letter, img in dictionary.items():
            if img.shape[0] > self.line_height:
                self.line_height = img.shape[0]
            self.letter_sizes[letter] = (img.shape[1], img.shape[0])

    def read_line(self, inp_img: np.ndarray, top:int = None, ref = None, max_dist_left:int = None, max_dist_right:int = None, sequence_tol:int = 5, cast_values:bool = True) -> dict:
        """
        Reads a line, so the output is a list of all the sequences (str or int) found on that line.
        :param inp_img: the reference image (eg. a screenshot or cropped section)
        :param top: if defined, the line will start on this top of the inp_img.
        :param ref: a pattern that, if defined instead of top, will serve to define the region of interest of the line (roi).
        :param max_dist_right: together with ref, crops the line from the right-side of ref.
        :param max_dist_left: together with ref, crops the line from the left-side of ref.
        :param sequence_tol: maximum separation between letters to be considered of the same sequence
        :param cast_values: if True (default), then the numbers are casted to int.
        """
        left = 0
        width = inp_img.shape[1]
        if top is None:
            if not ref is None:
                res = cv2.matchTemplate(inp_img, ref, cv2.TM_CCOEFF_NORMED, mask=alpha_to_mask(ref))
                np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val > 0.68:
                    top = max_loc[1]
                    if max_dist_left:
                        left = max(left, max_loc[0] - max_dist_left)
                    if max_dist_right:
                        width = min(width, ref.shape[1] + max_dist_right)                        
                else:
                    return None
            else:
                raise Exception("Must define a ref pattern or the top of the line to read")

        rx, ry, rw, rh = [left, top - 2, width, self.line_height + 6]
        inp_img = inp_img[ry:ry + rh, rx:rx + rw]

        # cv2.imshow("debug", inp_img)
        # cv2.waitKey(100000)

        letter_positions = OrderedDict()
        for letter, letter_pattern in self.dictionary.items():
            res = cv2.matchTemplate(inp_img, letter_pattern, cv2.TM_CCOEFF_NORMED)#, mask=alpha_to_mask(ref))
            np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
            y_positions, x_positions = np.where(res >= 0.85)
            if(len(x_positions)) == 0:
                continue
            # Remove overlapping letters.
            bboxes = []
            for i in range(len(x_positions)):
                bboxes.append([
                    x_positions[i],
                    y_positions[i],
                    x_positions[i] + self.letter_sizes[letter][0],
                    y_positions[i] + self.letter_sizes[letter][1]
                ])
            bboxes = LetterSequencesOCR.non_max_suppression_fast(np.array(bboxes), 0.5)
            for bbox in bboxes:
                letter_positions[bbox[0]] = letter
            # letter_positions[letter] = []
            # for bbox in bboxes:
            #     letter_positions[letter].append(bbox[0])
            # letter_positions[letter] = sorted(letter_positions[letter])

        letter_positions = OrderedDict(sorted(letter_positions.items(), key=lambda x: x[0]))
        sequences = []
        last_letter_pos_end = -999
        sequence = ""
        for letter_pos_start, letter in letter_positions.items():
            if letter_pos_start - last_letter_pos_end > sequence_tol:
                if len(sequence) > 0:
                    sequences.append(sequence)
                    sequence = ""
            last_letter_pos_end = letter_pos_start + self.letter_sizes[letter][0]
            sequence += letter
        if(len(sequence)) > 0:
            sequences.append(sequence)

        if cast_values:
            for i in range(len(sequences)):
                if sequences[i].isdigit():
                    sequences[i] = int(sequences[i])
            
        return sequences

    @staticmethod
    def non_max_suppression_fast(boxes, overlapThresh):
        """
        Helper function to remove duplicate bounding boxes.
        Source: Malisiewicz et al.
        """

        # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []
        # if the bounding boxes integers, convert them to floats --
        # this is important since we'll be doing a bunch of divisions
        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")
        # initialize the list of picked indexes	
        pick = []
        # grab the coordinates of the bounding boxes
        x1 = boxes[:,0]
        y1 = boxes[:,1]
        x2 = boxes[:,2]
        y2 = boxes[:,3]
        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            # compute the width and height of the bounding box
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            # compute the ratio of overlap
            overlap = (w * h) / area[idxs[:last]]
            # delete all indexes from the index list that have
            idxs = np.delete(idxs, np.concatenate(([last],
			np.where(overlap > overlapThresh)[0])))
        # return only the bounding boxes that were picked using the
        # integer data type
        return boxes[pick].astype("int")


class ItemStatOCR(LetterSequencesOCR):
    def __init__(self,):
        dictionary = {}
        files = list_files_in_folder("assets\\ocr\\numbers")
        for file in files:
            letter = os.path.basename(file).split(".")[0]
            dictionary[letter] = cv2.imread(file)
        super().__init__(dictionary)



if __name__ == "__main__":

    inp_img = cv2.imread("test/assets/item_stat_ocr.png")
    reader = ItemStatOCR()

    template_img = load_template("assets/item_properties/getting_magic_items.png", 1.0, True)
    template_np = cv2.cvtColor(template_img, cv2.COLOR_BGRA2BGR)

    results = reader.read_line(inp_img, ref=template_np, max_dist_left=250)
    print(results)