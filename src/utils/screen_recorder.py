from screen import Screen
import cv2
import os
import keyboard


screen = Screen(1)

os.system("mkdir generated")

keyboard.wait("f11")
i = 0
while 1:
    img = screen.grab()
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    cv2.imshow("x", img)
    cv2.imwrite(f"generated/{i}.png", img)
    cv2.waitKey(1)
    i += 1
