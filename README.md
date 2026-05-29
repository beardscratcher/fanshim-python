# Fan Shim for Raspberry Pi

# Installing

Clone and run the install script — this handles all dependencies via apt and sets up a systemd service:

```bash
git clone https://github.com/beardscratcher/fanshim-python
cd fanshim-python
sudo ./examples/install-service.sh
```

The installer accepts options to tune the speed curve:

```bash
sudo ./examples/install-service.sh \
  --speed-steps "50:0,60:30,70:60,80:100" \
  --min-speed 20 \
  --delay 2 \
  --brightness 255
```

# Reference

Set up an instance of the `FanShim` class:

```python
from fanshim import FanShim
fanshim = FanShim()
```

## Fan

Set fan to a specific speed (0.0 = off, 1.0 = full):

```python
fanshim.set_fan_speed(0.75)  # 75% speed
```

Turn the fan fully on or off:

```python
fanshim.set_fan(True)
fanshim.set_fan(False)
```

Get current fan speed (returns float 0.0–1.0):

```python
fanshim.get_fan()
```

## LED

Fan Shim includes one RGB APA-102 LED.

Set it to any colour with:

```python
fanshim.set_light(r, g, b)
```

Arguments r, g and b should be numbers between 0 and 255. For example, full red:

```python
fanshim.set_light(255, 0, 0)
```

## Automatic Temperature Control

`examples/automatic.py` runs a control loop that maps CPU temperature to fan speed using a configurable step curve. Run it directly or via the systemd service installed by `install-service.sh`.

```bash
python3 examples/automatic.py --speed-steps "50:0,60:30,70:60,80:100" --verbose
```

The speed curve is defined as comma-separated `temp:speed%` breakpoints. Fan speed is linearly interpolated between steps. `--min-speed` sets a floor to prevent motor stall at low duty cycles.

# Changes in 0.1.0

### GPIO backend: RPi.GPIO → lgpio

`RPi.GPIO` is deprecated on Linux kernel 5.x+ and removed from the library. All GPIO and PWM control now uses `lgpio`, which is maintained and compatible with kernel 6.x character device GPIO.

**Impact:** `python3-lgpio` is required (installed via apt by `install-service.sh`). The `pin_button` and `button_poll_delay` constructor parameters are gone — button support has been removed entirely.

### PWM fan speed control

Fan control was binary (on/off). It is now variable speed via hardware PWM at 1000 Hz. The fan ramps up and down proportionally to temperature rather than switching abruptly, reducing wear from thermal cycling and lowering noise at moderate temperatures.

**Impact:** `set_fan_speed(float)` is the primary new API. `set_fan(bool)` still works as a wrapper. `get_fan()` now returns a `float` (0.0–1.0) instead of an `int` (0/1).

### Temperature→speed curve replaces thresholds

`automatic.py` previously used binary on/off thresholds (`--on-threshold`, `--off-threshold`). It now uses a configurable step curve (`--speed-steps`) with linear interpolation and a minimum speed floor (`--min-speed`) to prevent motor stall at low duty cycles.

**Impact:** All previous CLI args to `automatic.py` and `install-service.sh` have changed. Re-run `install-service.sh` to migrate.

### Modernised install script

`install-service.sh` now uses `apt` for system dependencies and a `--system-site-packages` venv for the fanshim library, avoiding PEP 668 pip conflicts on Debian Trixie / DietPi. It also stops and disables any previous service version before installing the new one.

# Alternate Software

* Fan SHIM in C, using WiringPi - https://github.com/flobernd/raspi-fanshim
* Fan SHIM in C++, using libgpiod - https://github.com/daviehh/fanshim-cpp
