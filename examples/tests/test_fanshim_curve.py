import pytest
from fanshim_curve import speed_for_temp, apply_min_speed, parse_speed_steps

STEPS = [(50.0, 0.0), (60.0, 30.0), (70.0, 60.0), (80.0, 100.0)]


def test_below_first_step():
    assert speed_for_temp(40.0, STEPS) == 0.0


def test_at_first_step():
    assert speed_for_temp(50.0, STEPS) == 0.0


def test_exact_mid_breakpoint():
    assert speed_for_temp(60.0, STEPS) == 30.0


def test_interpolated_midpoint():
    assert speed_for_temp(65.0, STEPS) == 45.0


def test_interpolated_quarter():
    assert speed_for_temp(62.5, STEPS) == 37.5


def test_at_last_step():
    assert speed_for_temp(80.0, STEPS) == 100.0


def test_above_last_step():
    assert speed_for_temp(90.0, STEPS) == 100.0


def test_min_speed_floors_low_nonzero():
    assert apply_min_speed(15.0, 20.0) == 20.0


def test_min_speed_passes_through_above_floor():
    assert apply_min_speed(30.0, 20.0) == 30.0


def test_min_speed_zero_floored_to_min():
    assert apply_min_speed(0.0, 20.0) == 20.0


def test_parse_speed_steps_basic():
    result = parse_speed_steps("50:0,60:30,70:60,80:100")
    assert result == [(50.0, 0.0), (60.0, 30.0), (70.0, 60.0), (80.0, 100.0)]


def test_parse_speed_steps_sorts():
    result = parse_speed_steps("80:100,50:0,60:30,70:60")
    assert result == [(50.0, 0.0), (60.0, 30.0), (70.0, 60.0), (80.0, 100.0)]
