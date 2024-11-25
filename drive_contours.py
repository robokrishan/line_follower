from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import sys
# import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(
    transform=Transform(hflip=True, vflip=True),
    main={'size': (640, 360)}  # Resolution: 640x360
)
picam2.configure(cam_config)
picam2.start()

# Create I2C bus and PCA9685 instance
i2c = busio.I2C(3, 2)
pca = PCA9685(i2c)

# Initialize PCA9685 and set PWM frequency
pca.frequency = 50  # Set frequency to 50Hz for servos/ESC

while True:
    # Capture frame from the camera
    frame = picam2.capture_array()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Define the 200x200 box in the center of the frame
    height, width = gray.shape
    center_x, center_y = width // 2, height // 2
    box_start_x, box_start_y = center_x - 100, center_y - 100
    box_end_x, box_end_y = center_x + 100, center_y + 100

    # Crop the 200x200 region
    roi = gray[box_start_y:box_end_y, box_start_x:box_end_x]

    # Threshold to detect the dark line (adjust threshold as needed)
    _, binary = cv2.threshold(roi, 50, 255, cv2.THRESH_BINARY_INV)

    # Morphological operations to clean up noise
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.erode(binary, kernel, iterations=5)
    binary = cv2.dilate(binary, kernel, iterations=9)

    # Find contours in the cropped region
    contours, hierarchy = cv2.findContours(binary.copy(),
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and center line if detected
    if len(contours) > 0:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Draw the bounding rectangle relative to the full frame
        cv2.rectangle(frame, 
                      (box_start_x + x, box_start_y + y), 
                      (box_start_x + x + w, box_start_y + y + h), 
                      (255, 0, 0), 2)
        
        box_l = box_start_x + x
        box_r = box_start_x + x + w

        # Draw a center line relative to the full frame
        cv2.line(frame, 
                 (box_start_x + x + w // 2, box_start_y + y), 
                 (box_start_x + x + w // 2, box_start_y + y + h), 
                 (0, 255, 0), 2)
        
        weight_l = (box_start_x + x + w) - box_l
        weight_r = box_r - (box_start_x + x + w)

        if weight_l > weight_r:
            val = int(weight_l / 200)
            steer = (val*203) + 203
        else:
            val = int(weight_r / 200)
            steer = 408 - (val*203)

        print(steer)
        pca.channels[7].duty_cycle = steer

    # Draw the green box indicating the region of interest
    cv2.rectangle(frame, 
                  (box_start_x, box_start_y), 
                  (box_end_x, box_end_y), 
                  (0, 255, 0), 2)

    # Display the processed frame
    cv2.imshow("Camera Feed", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
picam2.stop()
cv2.destroyAllWindows()
