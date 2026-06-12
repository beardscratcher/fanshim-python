def hysteresis(fan_on, temp, on_threshold, off_threshold):
    """Return new fan_on state using two-threshold hysteresis."""
    if fan_on and temp <= off_threshold:
        return False
    if not fan_on and temp >= on_threshold:
        return True
    return fan_on
