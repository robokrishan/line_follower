import smbus2
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import Transform
import time

# PCA9685 Default Address
I2C_ADDR = 0x40

# Registers
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# Define the steering channel and limits
STEERING_CHANNEL = 7  # Servo connected to channel 7
ESC_CHANNEL = 0  # ESC connected to channel 0
DUTY_MIN = 203  # Minimum pulse width for the servo
DUTY_MAX = 408  # Maximum pulse width for the servo
DUTY_THROTTLE = 320  # Fixed duty cycle for ESC (throttle)

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Initialize PCA9685
def set_pwm_freq(freq_hz):
    prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
    bus.write_byte_data(I2C_ADDR, MODE1, 0x10)  # Sleep mode
    bus.write_byte_data(I2C_ADDR, PRESCALE, prescale_val)
    bus.write_byte_data(I2C_ADDR, MODE1, 0x80)  # Restart

def set_pwm(channel, on, off):
    bus.write_byte_data(I2C_ADDR, LED0_ON_L + 4 * channel, on & 0xFF)
    bus.write_byte_data(I2C_ADDR, LED0_ON_L + 4 * channel + 1, on >> 8)
    bus.write_byte_data(I2C_ADDR, LED0_ON_L + 4 * channel + 2, off & 0xFF)
    bus.write_byte_data(I2C_ADDR, LED0_ON_L + 4 * channel + 3, off >> 8)

# Set PWM frequency to 50Hz for servos
set_pwm_freq(50)

# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_preview_configuration(
    transform=Transform(hflip=True, vflip=True),
    main={'size': (640, 360)}
)
picam2.configure(cam_config)
picam2.start()

# Define the 200x200 box
BOX_WIDTH, BOX_HEIGHT = 200, 200

# Send throttle command to ESC (constant throttle)
set_pwm(ESC_CHANNEL, 0, DUTY_THROTTLE)
print(f"Throttle Duty Cycle: {DUTY_THROTTLE}")

while True:
    # Capture frame from the camera
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Define the region of interest (ROI)
    height, width = gray.shape
    center_x, center_y = width // 2, height // 2
    box_start_x, box_start_y = center_x - BOX_WIDTH // 2, center_y - BOX_HEIGHT // 2
    box_end_x, box_end_y = center_x + BOX_WIDTH // 2, center_y + BOX_HEIGHT // 2

    roi = gray[box_start_y:box_end_y, box_start_x:box_end_x]

    # Threshold and detect contours
    _, binary = cv2.threshold(roi, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # Find the largest contour and its center x-coordinate
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        line_center_x = x + w // 2

        # Normalize the x-coordinate (-1 to 1)
        normalized_position = (line_center_x - BOX_WIDTH // 2) / (BOX_WIDTH // 2)

        # Map normalized position to servo pulse width
        pulse_width = int(DUTY_MIN + (normalized_position + 1) * (DUTY_MAX - DUTY_MIN) / 2)

        # Send command to steering servo
        set_pwm(STEERING_CHANNEL, 0, pulse_width)

        print(f"Line Center: {line_center_x}, Normalized: {normalized_position}, Pulse Width: {pulse_width}")

        # Draw the bounding box and center line
        cv2.rectangle(frame, (box_start_x, box_start_y), (box_end_x, box_end_y), (0, 255, 0), 2)
        cv2.line(frame, (box_start_x + line_center_x, box_start_y), 
                 (box_start_x + line_center_x, box_end_y), (0, 255, 0), 2)


    # Display the processed frame
    cv2.imshow("Camera Feed", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
picam2.stop()
cv2.destroyAllWindows()
