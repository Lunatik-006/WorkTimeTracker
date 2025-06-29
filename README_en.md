# Pomodoro Timer

A simple desktop tool to organise your work using the Pomodoro technique. Timers are stored on disk and can be edited through a graphical interface.

## Features

- Create any number of timer presets with custom activities
- Configure the duration of every activity and rest period
- Set how many sets should be executed
- Drag and drop activities to change their order
- Save presets to JSON files for later use
- Start timers in a dedicated window with start/pause/stop/next controls
- Optional voice notifications via the `pyttsx3` library

## Installation

1. Ensure you have Python 3 with Tkinter installed.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the program:
   ```bash
   python main.py
   ```

Saved timer configurations are placed in the `timers/` folder created automatically next to the scripts.

## Usage

1. Use **+ New Timer** to create a configuration or double-click an existing one to edit.
2. Fill in the name, optional description and the number of sets.
3. Add activities specifying their durations and drag them to reorder.
4. Configure rest times between activities and sets.
5. Press **Save** and then **Run** to start the timer.
6. While running use the controls to pause, stop or skip to the next phase.

The runner window shows the current activity name, remaining time and the current set. A notification appears when all sets are completed.
