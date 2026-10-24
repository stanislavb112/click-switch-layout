import pytest

from temperature import convert_temperature


def test_celsius_to_fahrenheit():
    assert convert_temperature(100, "c") == pytest.approx(212)
    assert convert_temperature(0, "c") == pytest.approx(32)


def test_fahrenheit_to_celsius():
    assert convert_temperature(212, "f") == pytest.approx(100)
    assert convert_temperature(-40, "f") == pytest.approx(-40)


def test_unknown_unit():
    with pytest.raises(ValueError):
        convert_temperature(1, "k")
