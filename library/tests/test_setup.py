import mock
import sys


def test_setup(lgpio, apa102, FanShim):
    fanshim = FanShim()

    lgpio.gpiochip_open.assert_called_once_with(0)
    lgpio.gpio_claim_output.assert_called_once_with(42, fanshim._pin_fancontrol)
    apa102.APA102.assert_called_once_with(1, 15, 14, None, brightness=0.05)


def test_led_disable(lgpio, apa102, FanShim):
    fanshim = FanShim(disable_led=True)

    lgpio.gpiochip_open.assert_called_once_with(0)
    lgpio.gpio_claim_output.assert_called_once_with(42, fanshim._pin_fancontrol)
    assert not apa102.APA102.called

    fanshim.set_light(0, 0, 0)  # must be a no-op, not raise


def test_set_fan_speed(lgpio, apa102, FanShim):
    fanshim = FanShim()
    result = fanshim.set_fan_speed(0.5)
    assert result == 0.5
    lgpio.tx_pwm.assert_called_with(42, 18, 1000, 50.0)


def test_set_fan_speed_clamp_high(lgpio, apa102, FanShim):
    fanshim = FanShim()
    result = fanshim.set_fan_speed(2.0)
    assert result == 1.0
    lgpio.tx_pwm.assert_called_with(42, 18, 1000, 100.0)


def test_set_fan_speed_clamp_low(lgpio, apa102, FanShim):
    fanshim = FanShim()
    result = fanshim.set_fan_speed(-1.0)
    assert result == 0.0
    lgpio.tx_pwm.assert_called_with(42, 18, 1000, 0.0)


def test_set_fan_on(lgpio, apa102, FanShim):
    fanshim = FanShim()
    fanshim.set_fan(True)
    lgpio.tx_pwm.assert_called_with(42, 18, 1000, 100.0)


def test_set_fan_off(lgpio, apa102, FanShim):
    fanshim = FanShim()
    fanshim.set_fan(False)
    lgpio.tx_pwm.assert_called_with(42, 18, 1000, 0.0)


def test_get_fan(lgpio, apa102, FanShim):
    fanshim = FanShim()
    fanshim.set_fan_speed(0.75)
    assert fanshim.get_fan() == 0.75


def test_get_fan_initial(lgpio, apa102, FanShim):
    fanshim = FanShim()
    assert fanshim.get_fan() == 0.0


def test_cleanup(lgpio, apa102, FanShim):
    fanshim = FanShim()
    fanshim._cleanup()
    lgpio.gpiochip_close.assert_called_once_with(42)
