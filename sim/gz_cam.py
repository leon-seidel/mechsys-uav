import base64
import cv2
import numpy as np
import subprocess
import json

from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def read_camera_frames():
    # Start the gz topic process
    process = subprocess.Popen(['gz', 'topic', '--echo', '--topic', '/camera', '--json-output'],
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
            
            model.predict(source=img, show=True)
            
            # if img is not None:
            #     cv2.imshow('feed', img)
            #     if cv2.waitKey(1) & 0xFF == ord('q'):
            #         break


# Usage example:
try:
    read_camera_frames()
except KeyboardInterrupt:
    print("Stopping camera feed...")
finally:
    cv2.destroyAllWindows()