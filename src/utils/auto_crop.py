"""
Script to autocrop items. Input image with items in the correct resolution and the script will auto crop it for you and ask for names for each of them.
"""
import argparse
import os
import cv2
import numpy as np
from config import Config
from utils.misc import color_filter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to autocrop items.")
    parser.add_argument("--file_path", type=str, help="Path to screenshots e.g. C:/data")
    parser.add_argument("--target_height", type=int, help="Target width of each item for the given resolution")
    parser.add_argument("--gausian_blur", type=int, help="Gausian blur should be adapted to target resolution e.g. (9, 5) is good for 1280x720")
    args = parser.parse_args()

    args.file_path = "C:\\git\\botty"
    args.target_height = 21
    args.gausian_blur = (17, 5)

    config = Config()
    color_ranges = {
        "white": config.colors["white"],
        "gray": config.colors["gray"],
        "magic": config.colors["blue"],
        "set": config.colors["green"],
        "rare": config.colors["yellow"],
        "unique": config.colors["gold"],
        "runes": config.colors["orange"]
    }

    for filename in os.listdir(args.file_path):
        if filename.endswith(".png"):
            img = cv2.imread(f"{args.file_path}\\{filename}")
            # img = inp_img[:,:,:]
            filtered_img = np.zeros(img.shape, np.uint8)
            for key in color_ranges:
                _, extracted_img = color_filter(img, color_ranges[key])
                filtered_img = cv2.bitwise_or(filtered_img, extracted_img)
            filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
            cluster_img = np.clip(cv2.GaussianBlur(filtered_img_gray, args.gausian_blur, cv2.BORDER_DEFAULT), 0, 255)
            contours = cv2.findContours(cluster_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.destroyAllWindows()
                cropped_item = img[y:y+h, x:x+w]
                display_item = cv2.resize(cropped_item, None, fx=4, fy=4)
                if args.target_height - 12 < h < args.target_height + 6:
                    _, mask = cv2.threshold(cropped_item, 5, 255, cv2.THRESH_BINARY_INV)
                    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                    new_cntr = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    new_cntr = new_cntr[0] if len(new_cntr) == 2 else new_cntr[1]
                    for cnt in new_cntr:
                        x, y, w, h = cv2.boundingRect(cnt)
                        # cv2.rectangle(cropped_item, (x, y), (x+w, y+h), (0, 255, 0), 1)
                        if args.target_height - 12 < h < args.target_height + 6:
                            sub_sampled_cropped_item = cropped_item[y:y+h, x+3:x+w-3]
                            display_item = cv2.resize(sub_sampled_cropped_item, None, fx=4, fy=4)
                            cv2.namedWindow("item")
                            cv2.moveWindow("item", 3000, 200)
                            cv2.imshow("item", display_item)
                            cv2.waitKey(1)
                            print("Input name and press enter...")
                            name = input()
                            if name != "":
                                cv2.imwrite(f"./generated/{name}.png", sub_sampled_cropped_item)
                            else:
                                print("Skipping")
                # else:
                #     cv2.imshow("bad", display_item)
                #     cv2.waitKey(0)
