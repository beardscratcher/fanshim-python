# examples/

Reference and development scripts. The active scripts (`automatic.py`, `install-service.sh`) live at the repo root.

## led.py

Cycles the APA-102 LED through the full HSV colour wheel. Useful for testing LED wiring and brightness.

```bash
python3 examples/led.py
```

## led2.py

Sweeps the LED through the temperature colour range (blue → green → red), previewing the colour scale used by `automatic.py`.

```bash
python3 examples/led2.py
```

## manual.py

FIFO-based fan and LED control. Reads commands from `/tmp/fanshim`:

```bash
echo "on"     > /tmp/fanshim   # fan full on
echo "off"    > /tmp/fanshim   # fan off
echo "FF0000" > /tmp/fanshim   # LED red
```

## button.py / toggle.py

**Reference only — button support has been removed from the library.**

These scripts document the original Pimoroni button API as a reference for any future re-implementation. They will not run against the current library.

Original API surface:

```python
fanshim = FanShim()
fanshim.set_hold_time(1.0)

@fanshim.on_press()
def press_handler():
    print("Pressed")

@fanshim.on_release()
def release_handler(was_held):
    if was_held:
        print("Long press.")
    else:
        print("Short press.")

@fanshim.on_hold()
def hold_handler():
    print("HELD")

# toggle_fan() returned and set the new bool state
state = fanshim.toggle_fan()
```

