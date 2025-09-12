# WorkTimeTracker

Набор небольших инструментов для продуктивной работы:

- Учет рабочего времени по простым текстовым логам с GUI и CLI (`workcounter`).
- Настраиваемый таймер по технике Помодоро с голосовыми уведомлениями (`pomodortimer`).
- Фоновый «шум»/эмбиент для работы — скачивание и бесшовное проигрывание звуковых петель (`bgr_noise`).

## Состав репозитория

- `workcounter/`: подсчет и визуализация рабочего времени из текстового лога.
  - Запуск GUI: `python workcounter/run_with_gui.py`
  - Запуск CLI: `python -m workcounter.worktime.cli path/to/log.txt`
  - Формат лога:
    - Дата строкой `YYYY.MM.DD`.
    - Внутри даты — строки времени `HH:MM Текст заметки` и/или строки только со временем для начала/окончания блока.
    - Пустая строка разделяет блоки.
    - Отдельные строки со статусами выставления и оплаты счета: `INVOICED` и `PAID` (между датами). По ним разбиваются периоды и считаются сводки.
  - Примеры логов смотрите в `workcounter/projects/`.
- `pomodortimer/`: графический Помодоро‑таймер на Tkinter.
  - Запуск: `python pomodortimer/main.py`
  - Профили таймеров хранятся в `timers/` (JSON-файлы). Поддерживаются голосовые оповещения через `pyttsx3`.
- `bgr_noise/`: утилиты для подготовки и проигрывания фонового шума.
  - Запуск: `python bgr_noise/main.py`
  - Требуется установленный `ffmpeg` в `PATH`. Конфигурация источников — `bgr_noise/pipeline_config.yaml`.
- `timers/`: пользовательские пресеты таймеров для `pomodortimer`.
- `settings.json`: общие настройки приложения (язык интерфейса, параметры TTS и т. п.).

## Требования и установка

- Нужен Python 3 с Tkinter.
- Зависимости ставятся по подпроектам:
  - `pip install -r workcounter/requirements.txt`
  - `pip install -r pomodortimer/requirements.txt`
  - `pip install -r bgr_noise/requirements.txt`

## Быстрый старт

- WorkCounter (GUI): `python workcounter/run_with_gui.py`
- WorkCounter (CLI): `python -m workcounter.worktime.cli workcounter/projects/FlowsTime.txt`
- Pomodoro Timer: `python pomodortimer/main.py`
- Background noise: `python bgr_noise/main.py`

## Дополнительно

Каждый подпроект имеет свой README с подробностями:

- `workcounter/README.md`
- `pomodortimer/README.md` (+ `README_en.md`, `README_ru.md`)
- `bgr_noise/README.md`

