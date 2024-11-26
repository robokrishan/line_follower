import smbus2
import time

# PCA9685 Default Address
I2C_ADDR = 0x40

# Registers
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# Define the steering channel and limits
STEERING_CHANNEL = 7        # Servo connected to channel 7
ESC_CHANNEL = 0             # ESC connected to channel 0
DUTY_MIN = 203              # Minimum pulse width for the servo
DUTY_MAX = 408              # Maximum pulse width for the servo
DUTY_THROTTLE = 320         # Fixed duty cycle for ESC (throttle)
DUTY_NEUTRAL = 307          # Neutral point for ESC & servo

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

def sweep(channel):
    print(f'Sweeping motor on channel {channel}...', end="")
    set_pwm(channel, 0, DUTY_NEUTRAL)

    for i in range(DUTY_NEUTRAL, DUTY_MIN, -5):
        set_pwm(channel, 0, i)
        time.sleep(0.4)

    for i in range(DUTY_MIN, DUTY_MAX, 5):
        set_pwm(channel, 0, i)
        time.sleep(0.4)

    for i in range(DUTY_MAX, DUTY_NEUTRAL, -5):
        set_pwm(channel, 0, i)
        time.sleep(0.4)

    print(' Done!')

# Initialize I2C bus
bus = smbus2.SMBus(1)

if __name__ == '__main__':
    set_pwm_freq(50)
    set_pwm(STEERING_CHANNEL, 0, 307)
    time.sleep(2)
    sweep(STEERING_CHANNEL)
    sweep(ESC_CHANNEL)

    print('PCA9685 module test complete.')
    