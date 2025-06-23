import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from worktime.counter import TimeCounter

ROOT = os.path.dirname(os.path.dirname(__file__))
LOG_PATH = os.path.join(ROOT, 'FlowsTime.txt')

def test_parse_periods_splits_on_status_lines():
    tc = TimeCounter(LOG_PATH)
    periods = tc.parse_periods()
    # Ensure separate periods are produced for each payment line
    assert len(periods) == 4
    assert periods[0]['status'].endswith('ОПЛАЧЕНО')
    assert periods[1]['status'].endswith('ОПЛАЧЕНО')
    assert periods[2]['status'].endswith('ОПЛАЧЕНО')


def test_no_separators_outside_work_blocks():
    tc = TimeCounter(LOG_PATH)
    lines = tc.intervals_with_statuses()
    # dash should appear only between first two intervals of the first day
    assert lines[1] == '------------'
    assert lines[3] != '------------'  # no dash after the last interval of the day
