from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np

# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(
    transform=Transform(hflip=True, vflip=True),
    main={'size': (640, 360)}
)
picam2.configure(cam_config)
picam2.start()

while True:
    # Capture frame from the camera
    frame = picam2.capture_array()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Apply a mask to define the region of interest (ROI)
    mask = np.ones_like(gray) * 255  # Create a white mask (255 = included, 0 = excluded)
    mask[:, :150] = 0  # Exclude pixels from column 0 to 150
    mask[:, 500:] = 0  # Exclude pixels from column 500 to 640

    # Apply the mask to the grayscale image
    roi = cv2.bitwise_and(gray, mask)

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

        # Draw the bounding rectangle
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
