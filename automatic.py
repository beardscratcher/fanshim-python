#!/usr/bin/env python3
import argparse
import signal
import sys
import time

import psutil

from fanshim import FanShim
from fan_control import hysteresis

parser = argparse.ArgumentParser()
parser.add_argument('--on-threshold', type=float, default=50.0,
                    help='Temperature in °C to turn the fan on. Default: 50.0')
parser.add_argument('--off-threshold', type=float, default=40.0,
                    help='Temperature in °C to turn the fan off. Default: 40.0')
parser.add_argument('--on-debounce', type=int, default=1,
                    help='Consecutive readings above on-threshold before fan starts. Default: 1')
parser.add_argument('--delay', type=float, default=2.0,
                    help='Seconds between temperature readings')
parser.add_argument('--noled', action='store_true', default=False,
                    help='Disable LED control')
parser.add_argument('--brightness', type=float, default=128.0,
                    help='LED brightness 0-255')
parser.add_argument('--verbose', action='store_true', default=False,
                    help='Print temperature and fan state each cycle')

args = parser.parse_args()

fanshim = FanShim(disable_led=args.noled)

fan_on = False
readings_above = 0
fanshim.set_fan_speed(0.0)

_last_temp = None


def clean_exit(signum, frame):
    fanshim.set_fan_speed(0.0)
    if not args.noled:
        fanshim.set_light(0, 0, 0)
    sys.exit(0)


def get_cpu_temp():
    global _last_temp
    t = psutil.sensors_temperatures()
    for name in ['cpu-thermal', 'cpu_thermal']:
        if name in t:
            _last_temp = t[name][0].current
            return _last_temp
    if _last_temp is not None:
        print(f"Warning: CPU temp sensor unavailable, holding last reading ({_last_temp:.1f}°C)")
        return _last_temp
    print("Warning: CPU temp sensor unavailable and no prior reading — skipping cycle")
    return None


# Colour stops mirroring DietPi's MOTD temperature bands.
_TEMP_COLOURS = [
    (30, (0, 255, 255)),   # cyan  — cool runnings
    (40, (0, 255, 0)),     # green — optimal
    (50, (255, 255, 0)),   # yellow — running warm
    (60, (255, 95, 0)),    # orange — running hot
    (70, (255, 0, 0)),     # red   — warning
]


def update_led(temp):
    if temp <= _TEMP_COLOURS[0][0]:
        r, g, b = _TEMP_COLOURS[0][1]
    elif temp >= _TEMP_COLOURS[-1][0]:
        r, g, b = _TEMP_COLOURS[-1][1]
    else:
        for i in range(len(_TEMP_COLOURS) - 1):
            t0, c0 = _TEMP_COLOURS[i]
            t1, c1 = _TEMP_COLOURS[i + 1]
            if t0 <= temp <= t1:
                ratio = (temp - t0) / (t1 - t0)
                r = int(c0[0] + ratio * (c1[0] - c0[0]))
                g = int(c0[1] + ratio * (c1[1] - c0[1]))
                b = int(c0[2] + ratio * (c1[2] - c0[2]))
                break
    scale = args.brightness / 255.0
    fanshim.set_light(int(r * scale), int(g * scale), int(b * scale))


signal.signal(signal.SIGTERM, clean_exit)

try:
    while True:
        temp = get_cpu_temp()
        if temp is None:
            time.sleep(args.delay)
            continue

        new_fan_on = hysteresis(fan_on, temp, args.on_threshold, args.off_threshold)

        if not fan_on and new_fan_on:
            readings_above += 1
            if readings_above >= args.on_debounce:
                fan_on = True
                readings_above = 0
                fanshim.set_fan_speed(1.0)
        elif fan_on and not new_fan_on:
            fan_on = False
            readings_above = 0
            fanshim.set_fan_speed(0.0)
        else:
            readings_above = 0

        if args.verbose:
            print(f"Temp: {temp:.1f}°C, Fan: {'on' if fan_on else 'off'}")

        if not args.noled:
            update_led(temp)

        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
