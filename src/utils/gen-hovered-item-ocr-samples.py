if __name__ == "__main__":
    import keyboard
    import cv2
    import os
    import time
    from screen import start_detecting_window, stop_detecting_window, grab
    from d2r_image.processing_helpers import crop_text_clusters, crop_item_tooltip
    from d2r_image.data_models import ItemText
    from logger import Logger
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    Logger.info("Move to d2r window and press f11")
    keyboard.wait("f11")

    while 1:
        o_img = grab()
        img = o_img.copy()

        res, quality = crop_item_tooltip(img)
        res : ItemText
        if res.ocr_result:
            contours = crop_text_clusters(res.img)
            for contour in contours:
                contour : ItemText

                basename = f"generated/ground-truth/{time.strftime('%Y%m%d_%H%M%S')}"
                cv2.imshow(time.strftime('%Y%m%d_%H%M%S'), res.img)
                cv2.waitKey(1)
                print(f"new template: {basename} = ")
                print(f"Enter true text:")
                truth = input()
                if truth:
                    with open(f"{basename}.gt.txt", 'w') as f:
                        f.write(truth)
                    cv2.imwrite(f"{basename}.png", template_img)
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                    print(f"saved {basename}")
                else:
                    print(f"skipped {basename}")