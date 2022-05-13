import cv2

class ScreenMock():
    def __init__(self, filename):
        self._filename = filename
        
    def grab(self):
        img = cv2.imread(self._filename)
        return img
