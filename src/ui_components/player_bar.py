# f: get_experience
# - belt_row_1
from config import Config
from screen import convert_screen_to_monitor, grab
from utils.custom_mouse import mouse
from utils.misc import cut_roi
from logger import Logger
from config import Config
from ocr import Ocr

def get_experience():
    # mouseover exp bar
    pos=(Config().ui_pos["xp_bar_x"], Config().ui_pos["xp_bar_y"])
    x_m, y_m =  convert_screen_to_monitor(screen_coord = pos)
    mouse.move(x_m, y_m, randomize = (80,1))
    # crop roi
    img = grab()
    crop = cut_roi(img, Config().ui_roi["xp_bar_text"])
    ocr_result = Ocr().image_to_text(
        images = crop,
        model = "engd2r_inv_th",
        psm = 7,
        scale = 1.3,
        crop_pad = True,
        erode = True,
        invert = True,
        digits_only = False,
        fix_regexps = False,
        check_known_errors = False,
        check_wordlist = False,
        word_match_threshold = 0.9
    )[0]
    Logger.debug(ocr_result.text)

if __name__ == "__main__":
    exp = get_experience()
