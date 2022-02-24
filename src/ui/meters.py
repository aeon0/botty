import cv2
import numpy as np
from utils.misc import cut_roi, color_filter
from config import Config

def get_health(img: np.ndarray) -> float:
    # red mask
    health_img = cut_roi(img, Config().ui_roi["health_slice"])
    mask, _ = color_filter(health_img, Config().colors["health_globe_red"])
    health_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
    # green (in case of poison)
    mask, _ = color_filter(health_img, Config().colors["health_globe_green"])
    health_percentage_green = (float(np.sum(mask)) / mask.size) * (1/255.0)
    return max(health_percentage, health_percentage_green)

def get_mana(img: np.ndarray) -> float:
    mana_img = cut_roi(img, Config().ui_roi["mana_slice"])
    mask, _ = color_filter(mana_img, Config().colors["mana_globe"])
    mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
    return mana_percentage

def get_merc_health(img: np.ndarray) -> float:
    health_rec = [Config().ui_pos["merc_health_left"], Config().ui_pos["merc_health_top"], Config().ui_pos["merc_health_width"], 1]
    merc_health_img = cut_roi(img, health_rec)
    merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
    merc_health_percentage = (float(np.sum(thresh)) / thresh.size) * (1/255.0)
    return merc_health_percentage