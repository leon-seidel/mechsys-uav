import base64
import threading
import cv2
import numpy as np
import subprocess
import json

def read_camera_frames():
    # Start the gz topic process
    topic = '/world/baylands/model/x500_mono_cam_down_1/link/camera_link/sensor/imager/image'
    process = subprocess.Popen(['gz', 'topic', '--echo', '--topic', topic, '--json-output'],
                             stdout=subprocess.PIPE,
                             text=True)
    
    while True:
        # Read line by line
        line = process.stdout.readline()
        if line:
            # Parse JSON data
            data = json.loads(line)

            # Extract image data
            width = data['width']
            height = data['height']
            pixels = data['data']

            # Convert bytes to numpy array
            img_array = np.frombuffer(base64.b64decode(pixels), dtype=np.uint8)
            # Reshape array to image dimensions
            img = img_array.reshape((height, width, 3))
            
            # Convert from RGB to BGR (OpenCV uses BGR by default)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            img = cv2.resize(img, (320, 240))
            yield img


class GZCamera:
    def __init__(self, show_image=True):
        self._stop_event = threading.Event()
        self._latest_image = None
        self._thread = None
        self.show_image = show_image
        self.K = np.array([[152, 0,   160],
                           [0,   152, 120],
                           [0,   0,   1]])

    def _camera_loop(self):
        for img in read_camera_frames():
            self._latest_image = img
            if self.show_image:
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

