import threading
import cv2
import numpy as np
from picamera2 import Picamera2

def read_camera_frames():
    # Initialize the camera
    picam2 = Picamera2()
    # Configure the camera for 320x240 resolution
    config = picam2.create_video_configuration(
        main={"size": (320, 240)},
        controls={"FrameDurationLimits": (33333, 33333)}  # ~30fps
    )
    picam2.configure(config)
    picam2.start()
    
    while True:
        # Capture frame
        frame = picam2.capture_array()
        # Convert from RGB to BGR (OpenCV uses BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        yield frame


class PiCamera:
    def __init__(self):
        self._stop_event = threading.Event()
        self._latest_image = None
        self._thread = None
        self.K = np.array([[152, 0,   160],
                           [0,   152, 120],
                           [0,   0,   1]])

    def _camera_loop(self):
        for img in read_camera_frames():
            self._latest_image = img
            cv2.imshow('frame', img)
            cv2.waitKey(1)
            if self._stop_event.is_set():
                break

    def start(self):
        self._thread = threading.Thread(target=self._camera_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()

    def get_latest(self):
        return self._latest_image

