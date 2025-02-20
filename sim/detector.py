import cv2
import numpy as np

def detect_red_cross(image):
    # Read and convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range and threshold
    lower_red1 = np.array([0, 120, 120])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 120])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Morphological operations to reduce noise
    kernel = np.ones((2,2), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    for c in contours:
        # Approximate the shape
        approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        # Check if it could be a cross (e.g., 12-16 point approx shape)
        if 2 <= len(approx) <= 50:
            x, y, w, h = cv2.boundingRect(approx)
            center = (x + w//2, y + h//2)
            cv2.circle(image, center, 5, (255, 0, 0), -1)

    return image, center
