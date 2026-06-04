#!/usr/bin/env python3
import argparse
import signal
import sys
import time

import psutil

from fanshim import FanShim
from fanshim_curve import apply_min_speed, parse_speed_steps, speed_for_temp

parser = argparse.ArgumentParser()
parser.add_argument('--speed-steps', type=str, default='40:0,50:50,58:100',
                    help='Comma-separated temp:speed%% breakpoints e.g. "50:0,60:30,70:60,80:100"')
parser.add_argument('--min-speed', type=float, default=20.0,
                    help='Minimum fan speed %% when not fully off (prevents motor stall)')
parser.add_argument('--delay', type=float, default=2.0,
                    help='Seconds between temperature readings')
parser.add_argument('--noled', action='store_true', default=False,
                    help='Disable LED control')
parser.add_argument('--brightness', type=float, default=128.0,
                    help='LED brightness 0-255')
parser.add_argument('--verbose', action='store_true', default=False,
                    help='Print temperature and speed each cycle')

args = parser.parse_args()
steps = parse_speed_steps(args.speed_steps)

fanshim = FanShim(disable_led=args.noled)
fanshim.set_fan_speed(0.0)


def clean_exit(signum, frame):
    fanshim.set_fan_speed(0.0)
    if not args.noled:
        fanshim.set_light(0, 0, 0)
    sys.exit(0)


def get_cpu_temp():
    t = psutil.sensors_temperatures()
    for name in ['cpu-thermal', 'cpu_thermal']:
        if name in t:
            return t[name][0].current
    print("Warning: Unable to get CPU temperature!")
    return 0.0


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
        raw_speed = speed_for_temp(temp, steps)
        speed = apply_min_speed(raw_speed, args.min_speed)
        fanshim.set_fan_speed(speed / 100.0)

        if args.verbose:
            print(f"Temp: {temp:05.2f}C  Speed: {speed:5.1f}%")

        if not args.noled:
            update_led(temp)

        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
