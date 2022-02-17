import cv2
import numpy as np
from utils.misc import cut_roi, color_filter
from config import Config

def get_health(img: np.ndarray) -> float:
    health_rec = [Config().ui_pos["health_left"], Config().ui_pos["health_top"], Config().ui_pos["health_width"], Config().ui_pos["health_height"]]
    health_img = cut_roi(img, health_rec)
    # red mask
    mask1, _ = color_filter(health_img, [np.array([0, 110, 20]), np.array([2, 255, 255])])
    mask2, _ = color_filter(health_img, [np.array([178, 110, 20]), np.array([180, 255, 255])])
    mask = cv2.bitwise_or(mask1, mask2)
    health_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
    # green (in case of poison)
    mask, _ = color_filter(health_img, [np.array([47, 90, 20]), np.array([54, 255, 255])])
    health_percentage_green = (float(np.sum(mask)) / mask.size) * (1/255.0)
    return max(health_percentage, health_percentage_green)

def get_mana(img: np.ndarray) -> float:
    mana_rec = [Config().ui_pos["mana_left"], Config().ui_pos["mana_top"], Config().ui_pos["mana_width"], Config().ui_pos["mana_height"]]
    mana_img = cut_roi(img, mana_rec)
    mask, _ = color_filter(mana_img, [np.array([117, 120, 20]), np.array([121, 255, 255])])
    mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
    return mana_percentage