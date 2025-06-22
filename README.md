# Pomodoro Timer

This application provides a simple way to organise repetitive activity
cycles using the Pomodoro technique. You can create any number of custom
activity sets, store them on disk and run them using a graphical
interface.

## Features

* Configure an arbitrary list of activities with individual durations
* Specify rest periods between activities and between sets
* Save multiple timer configurations to JSON files
* Drag and drop activities to reorder them
* Run timers in a dedicated window with start/pause/stop controls

## Installation

This project requires Python 3 with Tkinter installed. Clone the
repository and run the application using:

```bash
python main.py
```

Timer configurations are stored in the `timers/` directory next to the
scripts.

## Usage

1. Press **New** to create a timer or select one from the list to edit.
2. Add activities and adjust their order.
3. Configure rest durations and the number of sets.
4. Save the timer and press **Run** to start.
5. Use the controls in the runner window to pause, stop or skip to the
   next activity.

During execution the application displays the current activity or rest
phase and a countdown timer. At the end of all sets you will receive a
notification.
