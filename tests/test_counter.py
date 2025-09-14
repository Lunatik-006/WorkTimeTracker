import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from worktime.counter import TimeCounter


def _write_log(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def test_parse_periods_splits_on_status_lines():
    log = """
2024.01.01

09:00 Work A
12:00

PAID

2024.01.02

10:00 Work B
12:00

PAID

2024.01.03

10:00 Work C
12:00

PAID

2024.01.04

10:00 Work D
12:00

INVOICED
""".strip()
    path = _write_log(log)
    tc = TimeCounter(path)
    periods = tc.parse_periods()
    assert len(periods) == 4
    assert periods[0]["status"].endswith("PAID")
    assert periods[1]["status"].endswith("PAID")
    assert periods[2]["status"].endswith("PAID")


def test_no_separators_outside_work_blocks():
    log = """
2024.01.05

09:00 First block
10:00

11:00 Second block
12:00
""".strip()
    path = _write_log(log)
    tc = TimeCounter(path)
    lines = tc.intervals_with_statuses()
    assert "------------" in lines
    assert lines[-1] != "------------"  # no dash after the last interval of the day


def test_no_empty_notes_at_edges():
    log = """
2024.01.06

09:00 Start
10:00

Some note line


11:00 End
12:00
""".strip()
    path = _write_log(log)
    tc = TimeCounter(path)
    periods = tc.parse_periods()
    for p in periods:
        for d in p.get("dates", []):
            if d.get("notes"):
                assert d["notes"][0] != ""
                assert d["notes"][-1] != ""
