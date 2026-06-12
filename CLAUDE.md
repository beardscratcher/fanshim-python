# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `fanshim-python`, a Python library for the [Pimoroni Fan Shim](https://www.pimoroni.com) hardware accessory for Raspberry Pi. It controls a fan (GPIO pin 18) via lgpio PWM and an RGB APA-102 LED (SPI via pins 14/15). Button support has been removed.

The library is in `fanshim-python/library/fanshim/__init__.py` — the entire public API lives in that single file (`FanShim` class). Hysteresis logic lives in `fan_control.py` at repo root (pure `hysteresis()` function, no hardware imports). `automatic.py` at repo root is the primary runnable script (on/off hysteresis control with LED colour feedback). `examples/` contains reference scripts only (LED demos, legacy button API).

**Deployment target:** Raspberry Pi 4 8GB, DietPi v10.4.2, Python 3.13, aarch64.

## Development Commands

All commands run from `fanshim-python/library/`. Use `python3 -m pytest` (not bare `pytest`) on macOS due to PEP 668.

```bash
# Run library tests
python3 -m pytest tests/ -v

# Run a single test
python3 -m pytest tests/test_setup.py::test_setup -v

# Run hysteresis tests (from repo root)
python3 -m pytest tests/ -v

# Lint check
flake8 --ignore E501

# Run tests with coverage
coverage run -m pytest tests/ -v && coverage report
```

From `fanshim-python/` (top-level):

```bash
# make check fails on macOS if __pycache__ dirs exist (BSD grep flags .pyc as binary matches)
find . -type d -name __pycache__ | xargs rm -rf && make check

```

## Testing Architecture

Tests run on non-Raspberry Pi machines by mocking hardware dependencies. `library/tests/conftest.py` provides fixtures that inject mocks for `lgpio`, `apa102`, `spidev`, and `atexit` into `sys.modules` before importing `FanShim`, then clean them up after each test. Test functions must explicitly declare which fixtures they need — none are autouse. `tests/conftest.py` (repo root) adds the repo root to `sys.path` so `fan_control` is importable without installation.

## Hardware / lgpio Constraints

- `lgpio.tx_pwm` max frequency: **10000 Hz** — we use 1000 Hz for fan PWM
- `apa102` unconditionally imports `RPi.GPIO` — the target needs `python3-rpi.gpio` (apt) even though our library uses lgpio directly
- On-device apt deps: `python3-lgpio python3-rpi.gpio python3-psutil python3-venv python3-spidev build-essential python3-dev`

## Hardware Pin Mapping

| Component | BCM Pin |
|-----------|---------|
| Fan control | 18 |
| LED data (SPI MOSI) | 14 |
| LED clock (SPI CLK) | 15 |

## Version Consistency

When bumping the version, update both `library/setup.cfg` (`version =`) and `library/fanshim/__init__.py` (`__version__ =`) — `make check` validates they match.

## Mirrored Defaults

`automatic.py` argparse defaults and `install-service.sh` shell variables must stay in sync — both define on-threshold, off-threshold, on-debounce, delay, brightness, and noled. Always update both files together.

## Fan On/Off Control Points

`automatic.py` calls `set_fan_speed()` in three places: startup (line ~34, sets 0.0), the `clean_exit` SIGTERM handler (sets 0.0), and the main loop (sets 1.0 on, 0.0 off). The fan is binary — no PWM partial speeds. Any change to fan behaviour at startup or shutdown must update both the startup call and `clean_exit`.

## Git Repository Root

The git repository root IS the working directory (`/Users/nick/Developer/fanshim`). Do NOT prefix paths with `fanshim-python/` — files like `automatic.py`, `fan_control.py`, and `install-service.sh` live at the repo root.

## On-Device Service Notes

- Service runs as root, files live at `/root/fanshim-python/`
- **Always run `install-service.sh` from inside `fanshim-python/`** — the script uses `$BASH_SOURCE` to compute `$DIR`, so running it from the wrong directory bakes an incorrect `ExecStart` path into the unit file, causing silent service failure on next reboot.
- DietPi sends SIGTERM to services during automated maintenance (~19:00 daily). "Deactivated successfully" in the journal is a clean stop, not a crash — the service restarts automatically via `Restart=on-failure`.
