from picamera2 import Picamera2
from libcamera import ColorSpace, Transform
import cv2
import numpy as np

picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(\
    transform=Transform(hflip=True, vflip=True),\
    main={'size':(1280, 720)})

picam2.configure(cam_config)
picam2.start()

while True:
    frame = picam2.capture_array()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 10, minLineLength=200, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(gray,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow("Camera Feed", gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


picam2.stop()
cv2.destroyAllWindows()