import lgpio
import apa102
import atexit

__version__ = '0.1.0'


class FanShim():
    def __init__(self, pin_fancontrol=18, disable_led=False):
        self._pin_fancontrol = pin_fancontrol
        self._fan_speed = 0.0
        self._disable_led = disable_led

        self._h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self._h, self._pin_fancontrol)

        if not self._disable_led:
            try:
                import RPi.GPIO as GPIO
                GPIO.setwarnings(False)
            except ImportError:
                pass
            self._led = apa102.APA102(1, 15, 14, None, brightness=0.05)

        atexit.register(self._cleanup)

    def get_fan(self):
        """Get current fan speed (0.0-1.0)."""
        return self._fan_speed

    def set_fan_speed(self, speed):
        """Set fan speed 0.0 (off) to 1.0 (full). Returns clamped value."""
        speed = max(0.0, min(1.0, float(speed)))
        self._fan_speed = speed
        lgpio.tx_pwm(self._h, self._pin_fancontrol, 1000, speed * 100)
        return speed

    def set_fan(self, fan_state):
        """Set fan on/off. Delegates to set_fan_speed."""
        return self.set_fan_speed(1.0 if fan_state else 0.0)

    def set_light(self, r, g, b, brightness=None):
        """Set LED colour. r, g, b: 0-255."""
        if self._disable_led:
            return
        self._led.set_pixel(0, r, g, b)
        if brightness is not None:
            self._led.set_brightness(0, brightness)
        self._led.show()

    def _cleanup(self):
        self.set_fan_speed(0.0)
        if not self._disable_led:
            self.set_light(0, 0, 0)
        lgpio.gpiochip_close(self._h)
