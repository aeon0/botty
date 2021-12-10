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

    args.file_path = "C:\\Users\\aliig\\Desktop\\bot\\botty-gleed-ocr\\input_images"
    gen_truth = 1


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
                if not gen_truth:
                    cv2.imwrite(f"./generated/z_{filename}_{key}_{count}.png", cluster.image)
                    cv2.rectangle(inp_img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    cv2.putText(inp_img, key, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                else:
                    cv2.namedWindow("item")
                    cv2.moveWindow("item", 100, 100)
                    cv2.imshow("item", cluster.image)
                    cv2.waitKey(1)
                    print("Input item name and press enter (converts to all caps)...")
                    item_name = input()
                    if item_name != "":
                        out_filename = f"{key}_{item_name.replace(' ','_')}"
                        if not os.path.exists(f"./ground_truth/{out_filename}.png"):
                            cv2.imwrite(f"./ground_truth/{out_filename}.png", cluster.image)
                            file1 = open(f"./ground_truth/{out_filename}.gt.txt","w")
                            file1.write(item_name.upper())
                            file1.close()
                    else:
                        print("Skipping")





            finish=time.time()
            print(f"{filename} total: {finish-start}s")
            #cv2.imwrite(f"./generated/{filename}.png", inp_img)
