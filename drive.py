from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
picam2.start_preview()
picam2.start()

while True:
    frame = picam2.capture_array()
    
    rgb = cv2.cvtColor(frame, 4)

    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


picam2.stop()
cv2.destroyAllWindows()