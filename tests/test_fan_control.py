import pytest
from fan_control import hysteresis


def test_fan_turns_on_at_threshold():
    assert hysteresis(False, 60.0, 60.0, 50.0) is True


def test_fan_does_not_turn_on_below_threshold():
    assert hysteresis(False, 59.9, 60.0, 50.0) is False


def test_fan_stays_on_in_hysteresis_band():
    # between off_threshold and on_threshold: state unchanged
    assert hysteresis(True, 55.0, 60.0, 50.0) is True


def test_fan_turns_off_at_off_threshold():
    assert hysteresis(True, 50.0, 60.0, 50.0) is False


def test_fan_does_not_turn_off_above_off_threshold():
    assert hysteresis(True, 50.1, 60.0, 50.0) is True


def test_fan_stays_off_in_hysteresis_band():
    assert hysteresis(False, 55.0, 60.0, 50.0) is False


def test_fan_stays_on_above_on_threshold():
    assert hysteresis(True, 70.0, 60.0, 50.0) is True
