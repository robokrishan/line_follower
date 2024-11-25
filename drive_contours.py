from picamera2 import Picamera2
from libcamera import ColorSpace, Transform
import cv2
import numpy as np

picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(\
    transform=Transform(hflip=True, vflip=True),\
    main={'size':(640, 360)})

picam2.configure(cam_config)
picam2.start()

while True:
    frame = picam2.capture_array()
    
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # blurred = cv2.imdecode(blurred, -1)

    black_line = cv2.inRange(frame, (0,0,0), (50,50,50))
    kernel = np.ones((3,3), np.uint8)

    black_line = cv2.erode(black_line, kernel, iterations=5)
    black_line = cv2.dilate(black_line, kernel, iterations=9)

    img, contours, hierarchy = cv2.findContours(black_line.copy(), \
                                                cv2.RETR_TREE, \
                                                cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        x, y, w, h = cv2.boundingRect(contours[0])
        cv2.line(gray, (x+(w/2), 200), (x+(w/2), 250),(255,0,0),3)

    cv2.imshow("Camera Feed", gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


picam2.stop()
cv2.destroyAllWindows()