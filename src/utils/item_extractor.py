"""
Script to autocrop items. Input image with items in the correct resolution and the script will auto crop it for you and ask for names for each of them.
"""
import argparse
import os
import cv2
import numpy as np
from config import Config
from utils.misc import color_filter
from item.item_cropper import ItemCropper
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to autocrop items.")
    parser.add_argument("--file_path", type=str, help="Path to screenshots e.g. C:/data")
    args = parser.parse_args()

    args.file_path = "C:\\Users\\aliig\\Desktop\\bot\\botty-prep-ocr\\input_images"

    item_cropper = ItemCropper()

    for filename in os.listdir(args.file_path):
        if filename.endswith(".png"):
            start = time.time()
            inp_img = cv2.imread(f"{args.file_path}\\{filename}")
            filename = filename[:-4]
            img = inp_img[:,:,:]
            item_clusters = item_cropper.crop(inp_img)
            for count, cluster in enumerate(item_clusters):
                x, y, w, h = cluster.roi
                key = cluster.color_key
                #cv2.imwrite(f"./generated/z_contours_{filename}_{key}_{count}.png", cropped_item)
                cv2.rectangle(inp_img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                cv2.putText(inp_img, key, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            finish=time.time()
            print(f"{filename} total: {finish-start}s")
            cv2.imwrite(f"./generated/{filename}.png", inp_img)
