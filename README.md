# timecounter

Simple command line utility that sums work time intervals from a log file.

## Usage

```
python timecounter.py path/to/log.txt
```

The tool prints the total hours since the last `ОПЛАЧЕНО` entry and, if the
log contains a subsequent `СЧЕТ ВЫСТАВЛЕН` line, also reports the hours that
were already invoiced but not yet paid.
