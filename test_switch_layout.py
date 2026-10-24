import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from switch_layout import (
    Base,
    convert_layout,
    count_translations,
    detect_direction,
    format_stat,
    format_stats,
    longest_text,
    save_translation,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# ---------- convert_layout / detect_direction ----------


def test_convert_en_to_ru():
    assert convert_layout("ghbdtn") == "привет"


def test_convert_ru_to_en():
    assert convert_layout("руддщ") == "hello"


def test_convert_keeps_uppercase():
    assert convert_layout("Ghbdtn") == "Привет"
    assert convert_layout("Руддщ") == "Hello"


def test_convert_punctuation_keys():
    assert convert_layout("[fkjn") == "халот"
    assert convert_layout("yf,.") == "набю"


def test_convert_keeps_spaces_and_digits():
    assert convert_layout("ghbdtn 123") == "привет 123"


def test_convert_is_reversible():
    assert convert_layout(convert_layout("ghbdtn vbh")) == "ghbdtn vbh"


def test_detect_direction():
    assert detect_direction("ghbdtn") == "en-ru"
    assert detect_direction("привет") == "ru-en"


def test_detect_direction_uses_majority_of_letters():
    assert detect_direction("приветt") == "ru-en"
    assert detect_direction("ghbdtnр") == "en-ru"


@pytest.mark.parametrize("text", ["", "   ", "123 !?"])
def test_no_letters_raises(text):
    with pytest.raises(ValueError):
        convert_layout(text)


# ---------- format_stat ----------


def test_format_stat_abs():
    assert format_stat(8, 12, "abs") == "8"


def test_format_stat_rel():
    assert format_stat(8, 12, "rel") == "66.7%"


def test_format_stat_both():
    assert format_stat(8, 12, None) == "8 (66.7%)"


def test_format_stat_zero_total():
    assert format_stat(0, 0, None) == "0 (0.0%)"


# ---------- база данных ----------


def test_count_translations_empty(session):
    assert count_translations(session) == {"en-ru": 0, "ru-en": 0}


def test_count_translations(session):
    save_translation(session, "en-ru", 5)
    save_translation(session, "en-ru", 7)
    save_translation(session, "ru-en", 3)
    assert count_translations(session) == {"en-ru": 2, "ru-en": 1}


def test_longest_text_none_when_empty(session):
    assert longest_text(session) is None


def test_longest_text(session):
    save_translation(session, "en-ru", 5)
    save_translation(session, "ru-en", 57)
    save_translation(session, "en-ru", 12)
    assert longest_text(session) == 57


def _fill(session):
    for _ in range(8):
        save_translation(session, "en-ru", 10)
    for _ in range(3):
        save_translation(session, "ru-en", 10)
    save_translation(session, "ru-en", 57)


def test_format_stats_both_views(session):
    _fill(session)
    assert format_stats(session, None) == [
        "en-ru: 8 (66.7%)",
        "ru-en: 4 (33.3%)",
        "Самый длинный текст: 57 символов",
    ]


def test_format_stats_abs(session):
    _fill(session)
    assert format_stats(session, "abs")[:2] == ["en-ru: 8", "ru-en: 4"]


def test_format_stats_rel(session):
    _fill(session)
    assert format_stats(session, "rel")[:2] == ["en-ru: 66.7%", "ru-en: 33.3%"]


def test_format_stats_longest_ignores_view(session):
    _fill(session)
    assert (
        format_stats(session, "abs")[-1]
        == format_stats(session, "rel")[-1]
        == "Самый длинный текст: 57 символов"
    )


def test_format_stats_empty_database(session):
    assert format_stats(session, None) == [
        "en-ru: 0 (0.0%)",
        "ru-en: 0 (0.0%)",
        "Самый длинный текст: нет данных",
    ]
