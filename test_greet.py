import pytest

from greet import build_greetings


def test_single_greeting_by_default_count():
    assert build_greetings("Аня", 1) == ["Привет, Аня!"]


def test_multiple_greetings():
    assert build_greetings("Аня", 3) == ["Привет, Аня!"] * 3


@pytest.mark.parametrize("times", [0, -1])
def test_rejects_non_positive_times(times):
    with pytest.raises(ValueError):
        build_greetings("Аня", times)
