from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np

picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(
    transform=Transform(hflip=True, vflip=True),
    main={'size': (1280, 720)}
)
picam2.configure(cam_config)
picam2.start()

while True:
    # Capture frame from the camera
    frame = picam2.capture_array()

    # Convert RGB to BGR (OpenCV expects BGR)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Detect black lines using inRange
    black_line = cv2.inRange(frame_bgr, (0, 0, 0), (50, 50, 50))

    # Morphological operations to clean up noise
    kernel = np.ones((3, 3), np.uint8)
    black_line = cv2.erode(black_line, kernel, iterations=5)
    black_line = cv2.dilate(black_line, kernel, iterations=9)

    # Find contours
    contours, hierarchy = cv2.findContours(black_line.copy(),
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding rectangle and center line if contours are detected
    if len(contours) > 0:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Draw the rectangle
        cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)

        p1 = (x + w // 2, y)
        p2 = (x + w // 2, y + h)

        # Draw a center line
        cv2.line(frame_bgr, p1, p2, (0, 255, 0), 2)

        offset = p1[0] - (1280/2)

        cv2.putText(frame_bgr, str(offset), (1150, 20),)

    # Display the processed frame
    cv2.imshow("Camera Feed", frame_bgr)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
picam2.stop()
cv2.destroyAllWindows()
