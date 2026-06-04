#!/usr/bin/env python3
import argparse
import colorsys
import signal
import sys
import time

import psutil

from fanshim import FanShim
from fanshim_curve import apply_min_speed, parse_speed_steps, speed_for_temp

parser = argparse.ArgumentParser()
parser.add_argument('--speed-steps', type=str, default='40:0,50:50,60:100',
                    help='Comma-separated temp:speed%% breakpoints e.g. "50:0,60:30,70:60,80:100"')
parser.add_argument('--min-speed', type=float, default=20.0,
                    help='Minimum fan speed %% when not fully off (prevents motor stall)')
parser.add_argument('--delay', type=float, default=2.0,
                    help='Seconds between temperature readings')
parser.add_argument('--noled', action='store_true', default=False,
                    help='Disable LED control')
parser.add_argument('--brightness', type=float, default=255.0,
                    help='LED brightness 0-255')
parser.add_argument('--verbose', action='store_true', default=False,
                    help='Print temperature and speed each cycle')

args = parser.parse_args()
steps = parse_speed_steps(args.speed_steps)
min_temp = steps[0][0]
max_temp = steps[-1][0]

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


def update_led(temp):
    ratio = (max(min_temp, min(max_temp, float(temp))) - min_temp) / (max_temp - min_temp)
    hue = (1.0 - ratio) * 120.0 / 360.0
    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(hue, 1.0, args.brightness / 255.0)]
    fanshim.set_light(r, g, b)


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
