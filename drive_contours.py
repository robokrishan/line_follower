from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np

# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(
    transform=Transform(hflip=True, vflip=True),
    main={'size': (640, 360)}  # Resolution: 640x360
)
picam2.configure(cam_config)
picam2.start()

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

    # Create a mask with the box region
    mask = np.zeros_like(gray)  # Black mask (all 0)
    mask[box_start_y:box_end_y, box_start_x:box_end_x] = 255  # White box

    # Apply the mask to the grayscale image
    roi = cv2.bitwise_and(gray, mask)

    # Draw the box on the frame for visualization
    cv2.rectangle(frame, (box_start_x, box_start_y), (box_end_x, box_end_y), (0, 255, 0), 2)

    # Threshold to detect the dark line (adjust threshold as needed)
    _, binary = cv2.threshold(roi, 50, 255, cv2.THRESH_BINARY_INV)

    # Morphological operations to clean up noise
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.erode(binary, kernel, iterations=5)
    binary = cv2.dilate(binary, kernel, iterations=9)

    # Find contours
    contours, hierarchy = cv2.findContours(binary.copy(),
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and center line if detected
    if len(contours) > 0:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Draw the bounding rectangle within the box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Draw a center line
        cv2.line(frame, (x + w // 2, y), (x + w // 2, y + h), (0, 255, 0), 2)

    # Display the processed frame
    cv2.imshow("Camera Feed", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
picam2.stop()
cv2.destroyAllWindows()
