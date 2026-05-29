"""Test configuration."""
import sys
import mock
import pytest


@pytest.fixture(scope='function', autouse=False)
def FanShim():
    """Yield the FanShim class with hardware modules mocked via other fixtures."""
    import fanshim
    yield fanshim.FanShim
    del sys.modules['fanshim']


@pytest.fixture(scope='function', autouse=False)
def lgpio():
    """Mock lgpio module."""
    lgpio = mock.MagicMock()
    lgpio.gpiochip_open.return_value = 42
    lgpio.SET_PULL_UP = 0
    sys.modules['lgpio'] = lgpio
    yield lgpio
    del sys.modules['lgpio']


@pytest.fixture(scope='function', autouse=False)
def apa102():
    """Mock APA102 module."""
    apa102 = mock.MagicMock()
    sys.modules['apa102'] = apa102
    yield apa102
    del sys.modules['apa102']


@pytest.fixture(scope='function', autouse=False)
def spidev():
    """Mock spidev module."""
    spidev = mock.MagicMock()
    sys.modules['spidev'] = spidev
    yield spidev
    del sys.modules['spidev']


@pytest.fixture(scope='function', autouse=False)
def atexit():
    """Mock atexit module."""
    atexit = mock.MagicMock()
    sys.modules['atexit'] = atexit
    yield atexit
    del sys.modules['atexit']
