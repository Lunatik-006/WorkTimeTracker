# WorkTimeTracker

Utility and GUI for summing work time intervals from a plain text log.

## Installation

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Command line usage

```bash
python timecounter.py path/to/log.txt
```

This prints the total hours since the last `ОПЛАЧЕНО` entry and, when the log
contains a following `СЧЕТ ВЫСТАВЛЕН` line, also reports already invoiced hours.
After displaying the statistics the tool allows you to mark the invoice as paid
or add new log lines.

## GUI

Launch the graphical interface with:

```bash
python run_gui.py
```

The GUI displays periods separated by statuses and visual breaks between work
blocks with dashed lines.
