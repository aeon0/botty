import cv2
from screen import Screen

class ScreenMock(Screen):
    def grab(self):
        img = cv2.imread("test/assets/hero_select.png")
        return img
