# utils/plate_color.py

import cv2
import numpy as np
from config.constants import color_ranges

def detect_plate_color(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
        if cv2.countNonZero(mask) > 0:
            return color
    return "unknown"
