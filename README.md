# Fan Shim for Raspberry Pi

# Hardware Requirements

| Component | Requirement |
|-----------|-------------|
| Board | Raspberry Pi 4 (tested: 8GB) |
| HAT | Pimoroni Fan Shim |
| OS | DietPi v10.4+ or Raspberry Pi OS (Debian Trixie/Bookworm) |
| Kernel | 5.x+ (tested: 6.18 aarch64) |
| Python | 3.11+ (tested: 3.13) |

> **Not tested on:** Raspberry Pi 3 or earlier, Pi 5, 32-bit OS images.

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

**Why:** `RPi.GPIO` is deprecated and unsupported on Linux kernel 5.x+. On kernel 6.x (Raspberry Pi OS / DietPi), it either fails silently or requires a compatibility shim. `lgpio` is the actively maintained replacement built on the modern kernel GPIO character device interface.

`RPi.GPIO` has been removed from the library. All GPIO and PWM control now uses `lgpio`.

**Impact:** `python3-lgpio` is required (installed via apt by `install-service.sh`). The `pin_button` and `button_poll_delay` constructor parameters are gone — button support has been removed entirely.

### PWM fan speed control

**Why:** Binary on/off fan control causes premature bearing wear from repeated full-speed spin-up and spin-down cycles. A fan that briefly hits 65°C and drops back to 58°C will cycle continuously, stressing the motor and creating noise. Variable PWM speed means the fan can maintain a low steady speed that keeps temperatures stable without cycling.

Fan control is now variable speed via PWM at 1000 Hz. The fan ramps proportionally to temperature rather than switching abruptly.

**Impact:** `set_fan_speed(float)` is the primary new API. `set_fan(bool)` still works as a wrapper. `get_fan()` now returns a `float` (0.0–1.0) instead of an `int` (0/1).

### Temperature→speed curve replaces thresholds

**Why:** A single on/off threshold requires tuning two values that fight each other (hysteresis). A step curve is more intuitive — define what speed you want at what temperature — and naturally handles the transition zone without oscillation.

`automatic.py` now uses a configurable step curve (`--speed-steps`) with linear interpolation and a minimum speed floor (`--min-speed`) to prevent motor stall at low duty cycles.

**Impact:** All previous CLI args to `automatic.py` and `install-service.sh` have changed. Re-run `install-service.sh` to migrate.

### Modernised install script

**Why:** Debian Trixie (the base for current DietPi and Raspberry Pi OS) enforces PEP 668, which prevents global `pip install`. The old script would fail with "externally managed environment" errors. Additionally, `RPi.GPIO` version checks via `pkg_resources` (also deprecated) would crash before the service was ever installed.

`install-service.sh` now uses `apt` for system dependencies and a `--system-site-packages` venv for the fanshim library. It also stops and disables any previous service version before installing the new one.

# Alternate Software

* Fan SHIM in C, using WiringPi - https://github.com/flobernd/raspi-fanshim
* Fan SHIM in C++, using libgpiod - https://github.com/daviehh/fanshim-cpp
