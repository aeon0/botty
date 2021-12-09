"""
Script to autocrop items. Input image with items in the correct resolution and the script will auto crop it for you and ask for names for each of them.
"""
import argparse
import os
import cv2
import numpy as np
from config import Config
from utils.misc import color_filter, cut_roi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to autocrop items.")
    parser.add_argument("--file_path", type=str, help="Path to screenshots e.g. C:/data")
    parser.add_argument("--target_height", type=int, help="Target width of each item for the given resolution")
    parser.add_argument("--gausian_blur", type=int, help="Gausian blur should be adapted to target resolution e.g. (9, 5) is good for 1280x720")
    args = parser.parse_args()

    args.file_path = "C:\\Users\\aliig\\Desktop\\bot\\botty-prep-ocr\\input_images"
    args.target_height = 21

    config = Config()

    gaus_filter = (19, 1)
    expected_height_range = [int(round(num, 0)) for num in [x / 1.5 for x in [14,40]]]
    expected_width_range = [int(round(num, 0)) for num in [x / 1.5 for x in [60,1280]]]

    hud_mask = cv2.imread(f"hud_mask.png")
    hud_mask = cv2.cvtColor(hud_mask, cv2.COLOR_BGR2GRAY)
    _,hud_mask = cv2.threshold(hud_mask, 1, 255, cv2.THRESH_BINARY)

    for filename in os.listdir(args.file_path):
        if filename.endswith(".png"):
            inp_img = cv2.imread(f"{args.file_path}\\{filename}")
            filename = filename[:-4]
            img = inp_img[:,:,:]
            # apply HUD mask
            if img.shape[0]==720 and img.shape[1]==1280:
                img = cv2.bitwise_and(img,img,mask=hud_mask)
            # find colors matching highlight item and change to black
            highlight_mask = color_filter(img, config.colors["item_highlight"])[0]
            img[highlight_mask > 0] = (0,0,0)
            # Cleanup image with erosion image as marker with morphological reconstruction
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)[1]
            kernel = np.ones((7,7),np.uint8)
            kernel2 = np.ones((3,3),np.uint8)
            marker = thresh.copy()
            marker[1:-1,1:-1] = 0
            while True:
                tmp=marker.copy()
                marker=cv2.dilate(marker, kernel2)
                marker=cv2.min(thresh, marker)
                difference = cv2.subtract(marker, tmp)
                if cv2.countNonZero(difference) == 0:
                    break
            mask_r=cv2.bitwise_not(marker)
            mask_color_r = cv2.cvtColor(mask_r, cv2.COLOR_GRAY2BGR)
            img=cv2.bitwise_and(img, mask_color_r)
            cv2.imwrite(f"./generated/{filename}_remove_borders.png", img)

            # Loop by item colors
            filtered_img = np.zeros(img.shape, np.uint8)
            game_color_ranges = ['white', 'gray', 'blue', 'green', 'yellow', 'gold', 'orange']
            for key in game_color_ranges:
                filtered_img = color_filter(img, config.colors[key])[1]
                filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
                # Cluster item names
                cluster_img = np.clip(cv2.GaussianBlur(filtered_img_gray, gaus_filter, cv2.BORDER_DEFAULT), 0, 255)
                contours = cv2.findContours(cluster_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = contours[0] if len(contours) == 2 else contours[1]
                for count, cntr in enumerate(contours):
                    x, y, w, h = cv2.boundingRect(cntr)
                    expected_height = 1 if (expected_height_range[0] < h < expected_height_range[1]) else 0
                    x -= 0
                    y = y-5 if y>5 else 0
                    w -= 0
                    h += 10
                    cropped_item = img[y:y+h, x:x+w]
                    # save most likely item drop contours
                    avg = int(np.average(cropped_item))
                    contains_black = 1 if np.min(cropped_item) < 14 else 0
                    expected_width = 1 if (expected_width_range[0] < w < expected_width_range[1]) else 0
                    mostly_dark = 1 if 7 < avg < 40 else 0
                    if contains_black and mostly_dark and expected_height and expected_width:
                        # double-check item color (gray/white and yellow/gold overlapping contours)
                        color_averages=[]
                        for key2 in game_color_ranges:
                            _, extracted_img2 = color_filter(cropped_item, config.colors[key2])
                            extr_avg = np.average(cv2.cvtColor(extracted_img2, cv2.COLOR_BGR2GRAY))
                            color_averages.append(extr_avg)
                        max_index = color_averages.index(max(color_averages))
                        item_type = game_color_ranges[max_index]
                        if item_type == key:
                            cv2.imwrite(f"./generated/z_contours_{filename}_{key}_{count}_{avg}.png", cropped_item)
                            cv2.rectangle(inp_img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                            cv2.putText(inp_img, key, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imwrite(f"./generated/{filename}.png", inp_img)
