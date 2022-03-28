import cv2
import WindowCapture
import numpy as np
import json
capture = WindowCapture.WindowCapture()
_hud_mask = cv2.imread(f"hud_mask.png", cv2.IMREAD_GRAYSCALE)
_hud_mask = cv2.threshold(_hud_mask, 1, 255, cv2.THRESH_BINARY)[1]
import keyboard
import os
class LiveViewer:
    def __init__(self):
        keyboard.add_hotkey('q', self.q_pressed)
        #with open('last_settings.json') as f:
        with open(r'd:\Documents\GitHub\botty-diablo\src\utils\live-view\last_settings.json') as f:
            self.settings = json.loads(f.read())
        self.setup()
        self.live_view(1)

    def q_pressed(self):
        os._exit(1)

    def setup(self):
        cv2.namedWindow("Settings", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Results", cv2.WINDOW_NORMAL)
        cv2.createTrackbar('erode', 'Settings', self.settings['erode'], 36, self.value_update)
        cv2.createTrackbar('dilate', 'Settings', self.settings['dilate'], 36, self.value_update)
        cv2.createTrackbar('blur', 'Settings', self.settings['blur'], 30, self.value_update)
        cv2.createTrackbar('lh', 'Settings', self.settings['lh'], 255, self.value_update)
        cv2.createTrackbar('ls', 'Settings', self.settings['ls'], 255, self.value_update)
        cv2.createTrackbar('lv', 'Settings', self.settings['lv'], 255, self.value_update)
        cv2.createTrackbar('uh', 'Settings', self.settings['uh'], 255, self.value_update)
        cv2.createTrackbar('us', 'Settings', self.settings['us'], 255, self.value_update)
        cv2.createTrackbar('uv', 'Settings', self.settings['uv'], 255, self.value_update)
        cv2.createTrackbar('bright', 'Settings', self.settings['bright'], 255, self.value_update)
        cv2.createTrackbar('contrast', 'Settings', self.settings['contrast'], 254, self.value_update)
        cv2.createTrackbar('thresh', 'Settings', self.settings['thresh'], 255, self.value_update)
        cv2.createTrackbar('invert', 'Settings', self.settings['invert'], 1, self.value_update)

    def bright_contrast(self, img, brightness=255, contrast=127):
        brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            al_pha = (max - shadow) / 255
            ga_mma = shadow
            cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
        else:
            cal = img

        if contrast != 0:
            alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            gamma = 127 * (1 - alpha)
            cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)
        return cal

    def value_update(self, ignore=0):
        self.image = capture.get_screenshot()
        self.image = cv2.bitwise_and(self.image, self.image, mask=_hud_mask)
        # black out character
        self.image = cv2.rectangle(self.image, (550,250), (700,400), (0,0,0), -1)
        try:
            self.settings['erode'] = cv2.getTrackbarPos('erode', 'Settings')
            self.settings['dilate'] = cv2.getTrackbarPos('dilate', 'Settings')
            self.settings['blur'] = cv2.getTrackbarPos('blur', 'Settings')
            self.settings['lh'] = cv2.getTrackbarPos('lh', 'Settings')
            self.settings['ls'] = cv2.getTrackbarPos('ls', 'Settings')
            self.settings['lv'] = cv2.getTrackbarPos('lv', 'Settings')
            self.settings['uh'] = cv2.getTrackbarPos('uh', 'Settings')
            self.settings['us'] = cv2.getTrackbarPos('us', 'Settings')
            self.settings['uv'] = cv2.getTrackbarPos('uv', 'Settings')
            self.settings['bright'] = cv2.getTrackbarPos('bright', 'Settings')
            self.settings['contrast'] = cv2.getTrackbarPos('contrast', 'Settings')
            self.settings['thresh'] = cv2.getTrackbarPos('thresh', 'Settings')
            self.settings['invert'] = cv2.getTrackbarPos('invert', 'Settings')
            with open('last_settings.json', 'w') as f:
                f.write(json.dumps(self.settings))
        except cv2.error:
            return
        if self.settings['erode']:
            kernel = np.ones((self.settings['erode'], self.settings['erode']), 'uint8')
            self.image = cv2.erode(self.image, kernel, None, iterations=1)
        if self.settings['dilate']:
            kernel = np.ones((self.settings['dilate'], self.settings['dilate']), 'uint8')
            self.image = cv2.dilate(self.image, kernel, iterations=1)

        if self.settings['blur']:
            self.image = cv2.blur(self.image, (self.settings['blur'], self.settings['blur']))
        self.image = self.bright_contrast(self.image, self.settings['bright'], self.settings['contrast'])
        lower = np.array([self.settings['lh'], self.settings['ls'], self.settings['lv']])
        upper = np.array([self.settings['uh'], self.settings['us'], self.settings['uv']])
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        cont_mask = cv2.inRange(self.hsv, lower, upper)
        self.image = cv2.bitwise_and(self.image, self.image, mask=cont_mask)
        if self.settings['thresh']:
            self.image = cv2.threshold(self.image, self.settings['thresh'], 255, cv2.THRESH_BINARY)[1]
        threshz = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        if self.settings['thresh']:
            _, threshz = cv2.threshold(threshz, self.settings['thresh'], 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.settings['invert']:
            self.image = 255 - self.image

        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(threshz)
        min_size = 40
        max_size = 200
        for i in range(1, n_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_size <= max_size:
                # print(stats[i, cv2.CC_STAT_AREA])
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                cv2.rectangle(self.image, (x, y), (x + w+5, y + h+5), (0, 255, 0), thickness=1)
        self.frame_markup = self.image.copy()
        cv2.imshow("Results", self.image)
        cv2.waitKey(1)

    def live_view(self, ignore):
        while True:
            self.value_update(1)

l = LiveViewer()