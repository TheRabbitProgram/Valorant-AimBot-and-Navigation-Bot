import time
import mss
import numpy as np
import cv2
import math
import keyboard

# Map Size 1.1
# Map Zoom 0.9

with mss.mss() as sct:
    while True:
        monitor = {"left": 50, "top": 25, "width": 375, "height": 400}
        mask = np.array(sct.grab(monitor))
        cv2.imshow("mask", mask)
        cv2.waitKey(100)
        if keyboard.is_pressed('x'):
            cv2.imwrite("Han.jpg", mask)
        if keyboard.is_pressed('='):
            cv2.destroyAllWindows()
            break
