# timecounter

Simple command line utility that sums work time intervals from a log file.

## Usage

```
python timecounter.py path/to/log.txt
```

The tool prints the total hours since the last `ОПЛАЧЕНО` entry and, if the
log contains a subsequent `СЧЕТ ВЫСТАВЛЕН` line, also reports the hours that
were already invoiced but not yet paid.

After displaying the calculated time, the program interactively offers to:

* mark the invoiced period as paid;
* mark the last unpaid period as invoiced;
* append additional log entries.

Any confirmed changes are immediately written back to the log file.
