# Fan Shim for Raspberry Pi

> **Fork of [pimoroni/fanshim-python](https://github.com/pimoroni/fanshim-python)**
>
> This fork modernises the library for Linux kernel 5.x / 6.x (Raspberry Pi OS / DietPi), where the original RPi.GPIO backend fails silently or requires a compatibility shim. Key changes: GPIO control migrated to **lgpio** (the actively maintained successor), **on/off hysteresis fan control** with configurable thresholds and debounce, LED colour feedback mirroring DietPi's temperature bands, and an updated install script compatible with the PEP 668 externally-managed Python environment on Debian Trixie.
>
> Button support has been removed. See [`examples/button.py`](examples/button.py) for the original API if you want to re-implement it.

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
sudo ./install-service.sh
```

The installer accepts options to tune the control loop:

```bash
sudo ./install-service.sh \
  --on-threshold 50 \
  --off-threshold 40 \
  --on-debounce 1 \
  --delay 2 \
  --brightness 128 \
  --noled
```

## Automatic Temperature Control

`automatic.py` runs a control loop that turns the fan on when temperature exceeds `--on-threshold` and off when it falls below `--off-threshold`. `--on-debounce` requires N consecutive above-threshold readings before the fan starts, preventing brief spikes from triggering the fan. The LED shows a colour gradient from cyan (cool) to red (hot). Run it directly or via the systemd service installed by `install-service.sh`.

```bash
python3 automatic.py --on-threshold 50 --off-threshold 40 --verbose
```

# Changes in 0.1.0

### GPIO backend: RPi.GPIO → lgpio

**Why:** `RPi.GPIO` is deprecated and unsupported on Linux kernel 5.x+. On kernel 6.x (Raspberry Pi OS / DietPi), it either fails silently or requires a compatibility shim. `lgpio` is the actively maintained replacement built on the modern kernel GPIO character device interface.

`RPi.GPIO` has been removed from the library. All GPIO and PWM control now uses `lgpio`.

**Impact:** `python3-lgpio` is required (installed via apt by `install-service.sh`). The `pin_button` and `button_poll_delay` constructor parameters are gone — button support has been removed entirely.

### On/off hysteresis fan control

**Why:** Variable PWM speed at partial duty cycles risks motor stall and is harder to reason about. Binary on/off with hysteresis is simpler and reliable: one threshold to turn on, a lower threshold to turn off, and a debounce counter to ignore brief spikes.

`automatic.py` uses `--on-threshold` / `--off-threshold` hysteresis with an optional `--on-debounce` count. The `set_fan_speed(float)` library API is retained (0.0–1.0), but `automatic.py` only ever calls it with 0.0 or 1.0.

**Impact:** `--speed-steps` and `--min-speed` have been removed. Re-run `install-service.sh` to migrate.

### LED colour feedback

The APA102 LED shows a continuous colour gradient mirroring DietPi's MOTD temperature bands: cyan (≤30°C) → green (40°C) → yellow (50°C) → orange (60°C) → red (≥70°C). Use `--noled` to disable.

### Modernised install script

**Why:** Debian Trixie (the base for current DietPi and Raspberry Pi OS) enforces PEP 668, which prevents global `pip install`. The old script would fail with "externally managed environment" errors. Additionally, `RPi.GPIO` version checks via `pkg_resources` (also deprecated) would crash before the service was ever installed.

`install-service.sh` now uses `apt` for system dependencies and a `--system-site-packages` venv for the fanshim library. It also stops and disables any previous service version before installing the new one.

# Alternate Software

* Fan SHIM in C, using WiringPi - https://github.com/flobernd/raspi-fanshim
* Fan SHIM in C++, using libgpiod - https://github.com/daviehh/fanshim-cpp

# Changelog
0.1.0
-----

* Replace RPi.GPIO with lgpio
* Add set_fan_speed for PWM control
* Remove button support

0.0.5
-----

* Replace Plasma API with APA102 library
* Add support for setting LED global brightness
* Add support for disabling button and/or LED
* Move packages/requires to setup.config, minimum version now Python 2.7

0.0.4
-----

* Prepare Fan SHIM to use legacy Plasma API

0.0.3
-----

* Fix: lower polling frequency and make customisable, for PR #6

0.0.2
-----

* Fix: Fix error on exit

0.0.1
-----

* Initial Release
