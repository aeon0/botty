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

    game_color_ranges = {
        "white": config.colors["white"],
        "gray": config.colors["gray"],
        "magic": config.colors["blue"],
        "set": config.colors["green"],
        "rare": config.colors["yellow"],
        "unique": config.colors["gold"],
        "runes": config.colors["orange"]
    }
    gaus_filter = (17, 1)

    expected_height_range = [int(round(num, 0)) for num in [x / 1.5 for x in [14,40]]]
    #expected_width_range = [int(round(num, 0)) for num in [x / 1.5 for x in [60,700]]]
    expected_width_range = [int(round(num, 0)) for num in [x / 1.5 for x in [60,1280]]]

    mask = cv2.imread(f"hud_mask.png")
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _,mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    for filename in os.listdir(args.file_path):
        if filename.endswith(".png"):
            inp_img = cv2.imread(f"{args.file_path}\\{filename}")
            filename = filename[:-4]
            img = inp_img[:,:,:]
            if img.shape[0]==720 and img.shape[1]==1280:
                img = cv2.bitwise_and(img,img,mask=mask)
            # Pre filter black and highlight
            mask1, _ = color_filter(img, config.colors["black"])
            mask2, _ = color_filter(img, config.colors["item_highlight"])
            filtered_img = cv2.bitwise_or(mask1, mask2)
            contours = cv2.findContours(filtered_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            new_img = np.zeros(img.shape, np.uint8)
            for cntr in contours:
                x, y, w, h = cv2.boundingRect(cntr)
                new_img[y:y+h, x:x+w] = img[y:y+h, x:x+w]
            img = new_img
            # Filter by item colors
            filtered_img = np.zeros(img.shape, np.uint8)
            for key in game_color_ranges:
                _, extracted_img = color_filter(img, game_color_ranges[key])
                filtered_img = cv2.bitwise_or(filtered_img, extracted_img)
            filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
            # Cluster item names
            cluster_img = np.clip(cv2.GaussianBlur(filtered_img_gray, gaus_filter, cv2.BORDER_DEFAULT), 0, 255)
            contours = cv2.findContours(cluster_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            for count, cntr in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cntr)
                x -= 0
                y = y-5 if y>5 else 0
                w -= 0
                h += 10
                cropped_item = img[y:y+h, x:x+w]
                # filter most likely item drop contours
                contains_black = 1 if np.min(cropped_item) < 14 else 0
                is_dark = 1 if np.average(cropped_item) < 45 else 0
                expected_height = 1 if (expected_height_range[0] < h < expected_height_range[1]) else 0
                expected_width = 1 if (expected_width_range[0] < w < expected_width_range[1]) else 0
                if contains_black and is_dark and expected_height and expected_width:
                    # determine item type
                    color_averages=[]
                    for key in game_color_ranges:
                        _, extracted_img2 = color_filter(cropped_item, game_color_ranges[key])
                        extr_avg = np.average(cv2.cvtColor(extracted_img2, cv2.COLOR_BGR2GRAY))
                        color_averages.append(extr_avg)
                    max_index = color_averages.index(max(color_averages))
                    item_type = list(game_color_ranges.keys())[max_index]

                    cv2.rectangle(inp_img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    cv2.putText(inp_img, item_type, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imwrite(f"./generated/{filename}.png", inp_img)
            #cv2.imshow(filename, inp_img)
            #cv2.waitKey()


                # cv2.destroyAllWindows()
                # cropped_item = img[y:y+h, x:x+w]
                # display_item = cv2.resize(cropped_item, None, fx=4, fy=4)
                # if args.target_height - 12 < h < args.target_height + 6:
                #     _, mask = cv2.threshold(cropped_item, 5, 255, cv2.THRESH_BINARY_INV)
                #     mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                #     new_cntr = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #     new_cntr = new_cntr[0] if len(new_cntr) == 2 else new_cntr[1]
                #     for cnt in new_cntr:
                #         x, y, w, h = cv2.boundingRect(cnt)
                #         # cv2.rectangle(cropped_item, (x, y), (x+w, y+h), (0, 255, 0), 1)
                #         if args.target_height - 12 < h < args.target_height + 6:
                #             sub_sampled_cropped_item = cropped_item[y:y+h, x+3:x+w-3]
                #             display_item = cv2.resize(sub_sampled_cropped_item, None, fx=4, fy=4)
                #             cv2.namedWindow("item")
                #             cv2.moveWindow("item", 3000, 200)
                #             cv2.imshow("item", display_item)
                #             cv2.waitKey(1)
                #             print("Input name and press enter...")
                #             name = input()
                #             if name != "":
                #                 cv2.imwrite(f"./generated/{name}.png", sub_sampled_cropped_item)
                #             else:
                #                 print("Skipping")
                # # else:
                # #     cv2.imshow("bad", display_item)
                # #     cv2.waitKey(0)
