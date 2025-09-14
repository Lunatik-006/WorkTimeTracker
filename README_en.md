# WorkTimeTracker

Clean, HR-friendly collection of small utilities I use to track time and improve focus. It’s split into 3 independent parts that can be run separately.

- workcounter: CLI + Tkinter GUI to sum work time from a plain text log and manage invoice markers.
- pomodortimer: Desktop Pomodoro timer with editable presets stored as JSON and optional TTS notifications.
- bgr_noise: Background noise pipeline that downloads audio from YouTube, makes seamless loops, and plays them.

## Quick Start

- Python 3 with Tkinter is required.
- Install dependencies for each subproject you want to try:
  - `pip install -r workcounter/requirements.txt`
  - `pip install -r pomodortimer/requirements.txt`
  - `pip install -r bgr_noise/requirements.txt`

## Run

- WorkCounter (GUI): `python workcounter/run_with_gui.py`
- WorkCounter (CLI): `python -m workcounter.worktime.cli workcounter/projects/FlowsTime.sample.txt`
- Pomodoro Timer: `python pomodortimer/main.py`
- Background Noise: `python bgr_noise/main.py`

## Notes

- No secrets, tokens or credentials are stored in this repository.
- User data is ignored by `.gitignore` (e.g., `timers/*.json`, personal logs under `workcounter/projects/`).
- See per-folder READMEs for details: `workcounter/README.md`, `pomodortimer/README_en.md`, `bgr_noise/README.md`.
