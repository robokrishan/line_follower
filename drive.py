from picamera2 import Picamera2
from libcamera import ColorSpace, Transform
import cv2

picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(\
    transform=Transform(hflip=True, vflip=True),\
    main={'size':(1280, 720)})

picam2.configure(cam_config)
picam2.start()

while True:
    frame = picam2.capture_array()
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Camera Feed", rgb)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


picam2.stop()
cv2.destroyAllWindows()