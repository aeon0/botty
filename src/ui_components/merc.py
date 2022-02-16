# - merc_portrait
# - merc_life

from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator
from config import Config
import numpy as np
import cv2
from utils.misc import cut_roi

@Locator(ref=["MERC_A2","MERC_A1","MERC_A5","MERC_A3"], roi="merc_icon", threshold=0.9)
class MercIcon(ScreenObject):
    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(template_finder, match)

def get_merc_health(img: np.ndarray) -> float:
    config = Config()
    health_rec = [config.ui_pos["merc_health_left"], config.ui_pos["merc_health_top"], config.ui_pos["merc_health_width"], 1]
    merc_health_img = cut_roi(img, health_rec)
    merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
    merc_health_percentage = (float(np.sum(thresh)) / thresh.size) * (1/255.0)
    return merc_health_percentage