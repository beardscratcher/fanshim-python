def speed_for_temp(temp, steps):
    """
    Interpolate fan speed from temperature.

    steps: sorted list of (temp_c, speed_percent) tuples.
    Returns speed 0.0-100.0, clamped to table bounds.
    """
    if temp <= steps[0][0]:
        return float(steps[0][1])
    if temp >= steps[-1][0]:
        return float(steps[-1][1])
    for i in range(len(steps) - 1):
        t0, s0 = steps[i]
        t1, s1 = steps[i + 1]
        if t0 <= temp <= t1:
            ratio = (temp - t0) / (t1 - t0)
            return s0 + ratio * (s1 - s0)
    return float(steps[-1][1])


def apply_min_speed(speed, min_speed):
    """Floor speed to min_speed — fan always runs, never stops."""
    return max(speed, float(min_speed))


def parse_speed_steps(steps_str):
    """Parse 'temp:speed,...' string into sorted list of (float, float) tuples."""
    steps = []
    for pair in steps_str.split(','):
        temp, speed = pair.strip().split(':')
        steps.append((float(temp), float(speed)))
    return sorted(steps, key=lambda x: x[0])
