import cv2

class ScreenMock():
    def grab(self):
        img = cv2.imread("test/assets/hero_select.png")
        return img
