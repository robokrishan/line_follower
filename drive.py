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

    edges = cv2.Canny(gray, 50, 200)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=200, maxLineGap=10)

    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(gray, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imshow("Camera Feed", gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


picam2.stop()
cv2.destroyAllWindows()