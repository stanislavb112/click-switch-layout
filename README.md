# TI232 — click (вариант 3: switch_layout)

**Студент:** Stanislav Basli
**Группа:** TI232r
**Вариант:** 3 (switch_layout, жёлтый)

## Что сделано

### switch_layout (вариант 3) + stats
Утилита-группа `click.group` — аналог Punto Switcher.

- `switch_layout convert` — берёт текст из буфера обмена (`pyperclip.paste()`),
  по алфавиту определяет, какая раскладка «перепутана» (больше кириллицы → `ru-en`,
  больше латиницы → `en-ru`), конвертирует в противоположную, копирует результат
  обратно в буфер и печатает его. Пустой буфер или текст без букв → `click.ClickException`.
- `switch_layout stats [--view abs|rel]` — сколько конвертаций `en-ru` и `ru-en`
  (абсолютные числа, проценты или оба вида, если `--view` не указан) и длина
  самого длинного текста (всегда одним числом).

Каждая конвертация пишется в sqlite (`stats.db`) через SQLAlchemy
(`DeclarativeBase`, `Base.metadata.create_all`): направление и длина исходного текста.

Логика вынесена в функции: `convert_layout`, `detect_direction`, `format_stat`,
`save_translation`, `count_translations`, `longest_text`, `format_stats`
(работа с базой принимает `Session` первым аргументом).

### Задания из лекции
- `greet NAME [--times/-t N]` — приветствие N раз.
- `temperature --value X --unit c|f` — конвертация °C ↔ °F
  (`--unit` — единица, в которой задано `--value`).

## Установка и запуск

```bash
pip install -r requirements.txt
pip install -e .          # даёт команды switch_layout, greet, temperature

# без установки пакета:
python switch_layout.py convert
python switch_layout.py stats
python switch_layout.py stats --view abs
python switch_layout.py stats --view rel
```

Пример: в буфере `ghbdtn` → `switch_layout convert` печатает `привет`.

```
$ python switch_layout.py stats
en-ru: 8 (66.7%)
ru-en: 4 (33.3%)
Самый длинный текст: 57 символов
```

## Тесты

```bash
pytest
```

Тесты — на «голые» функции (`test_switch_layout.py`, `test_greet.py`,
`test_temperature.py`); база для тестов — `sqlite:///:memory:`.
