"""switch_layout — аналог Punto Switcher: конвертирует текст из буфера обмена
в противоположную раскладку (ru <-> en) и ведёт статистику в sqlite."""

import re
from contextlib import contextmanager

import click
import pyperclip
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# --------------------------------------------------------------------------
# Чистая логика (без буфера обмена и без базы)
# --------------------------------------------------------------------------

EN_LOWER = "`qwertyuiop[]asdfghjkl;'zxcvbnm,./"
RU_LOWER = "ёйцукенгшщзхъфывапролджэячсмитьбю."
# EN_LOWER[i] и RU_LOWER[i] — одна физическая клавиша
assert len(EN_LOWER) == len(RU_LOWER)


def _build_table(src: str, dst: str) -> dict[int, str]:
    """Таблица для str.translate: строчные + заглавные (только у букв)."""
    pairs = {}
    for s, d in zip(src, dst):
        pairs[ord(s)] = d
        if s.isalpha():  # знаки препинания у "[" / ";" не имеют заглавной формы
            pairs[ord(s.upper())] = d.upper()
    return pairs


EN_TO_RU = _build_table(EN_LOWER, RU_LOWER)
RU_TO_EN = _build_table(RU_LOWER, EN_LOWER)

CYRILLIC_RE = re.compile(r"[а-яА-ЯёЁ]")
LATIN_RE = re.compile(r"[a-zA-Z]")

DIRECTIONS = ("en-ru", "ru-en")


def detect_direction(text: str) -> str:
    """Определяет направление конвертации по алфавиту.

    Больше кириллицы -> текст набран в русской раскладке, а нужен английский
    ("ru-en"); больше латиницы -> "en-ru".
    """
    cyrillic_count = len(CYRILLIC_RE.findall(text))
    latin_count = len(LATIN_RE.findall(text))
    if cyrillic_count == 0 and latin_count == 0:
        raise ValueError("в тексте нет ни кириллических, ни латинских букв")
    return "ru-en" if cyrillic_count > latin_count else "en-ru"


def convert_layout(text: str) -> str:
    """Переводит текст в противоположную раскладку."""
    direction = detect_direction(text)
    table = RU_TO_EN if direction == "ru-en" else EN_TO_RU
    return text.translate(table)


def format_stat(count, total, view):
    percent = count / total * 100 if total else 0
    if view == "abs":
        return f"{count}"
    if view == "rel":
        return f"{percent:.1f}%"
    return f"{count} ({percent:.1f}%)"  # view is None — оба вида


# --------------------------------------------------------------------------
# База данных (SQLAlchemy + sqlite)
# --------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(primary_key=True)
    direction: Mapped[str]  # "en-ru" или "ru-en"
    length: Mapped[int]  # длина исходного текста


def save_translation(session: Session, direction: str, length: int) -> None:
    session.add(Translation(direction=direction, length=length))
    session.commit()


def count_translations(session: Session) -> dict[str, int]:
    """Сколько переводов в каждом направлении (нули для отсутствующих)."""
    rows = session.execute(
        select(Translation.direction, func.count()).group_by(Translation.direction)
    ).all()
    counts = {direction: 0 for direction in DIRECTIONS}
    counts.update({direction: count for direction, count in rows})
    return counts


def longest_text(session: Session) -> int | None:
    """Длина самого длинного текста или None, если записей ещё нет."""
    return session.execute(select(func.max(Translation.length))).scalar()


def format_stats(session: Session, view: str | None) -> list[str]:
    counts = count_translations(session)
    total = sum(counts.values())
    lines = [
        f"{direction}: {format_stat(counts[direction], total, view)}"
        for direction in DIRECTIONS
    ]
    longest = longest_text(session)
    # длина — не доля, поэтому выводится всегда одним числом, независимо от --view
    lines.append(
        "Самый длинный текст: нет данных"
        if longest is None
        else f"Самый длинный текст: {longest} символов"
    )
    return lines


@contextmanager
def get_session():
    engine = create_engine("sqlite:///stats.db")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# --------------------------------------------------------------------------
# CLI — тонкая обёртка
# --------------------------------------------------------------------------


@click.group()
def cli():
    """switch_layout — конвертер раскладки клавиатуры (ru <-> en)."""


@cli.command()
def convert():
    """Конвертирует текст из буфера обмена в противоположную раскладку."""
    text = pyperclip.paste()
    if not text or not text.strip():
        raise click.ClickException("буфер обмена пуст")
    try:
        direction = detect_direction(text)
        result = convert_layout(text)
    except ValueError as error:
        raise click.ClickException(str(error))

    pyperclip.copy(result)
    with get_session() as session:
        save_translation(session, direction, len(text))
    click.echo(result)


@cli.command()
@click.option("--view", type=click.Choice(["abs", "rel"]), default=None)
def stats(view):
    """Статистика конвертаций: abs — числа, rel — проценты, без опции — оба вида."""
    with get_session() as session:
        for line in format_stats(session, view):
            click.echo(line)


if __name__ == "__main__":
    cli()
