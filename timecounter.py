"""Simple CLI tool for counting working time blocks in a log file.

The script sums time intervals between the first and last timestamp of each
block after the most recent "ОПЛАЧЕНО" status.  It also calculates the amount of
time already invoiced but not yet paid - the interval from the last
"ОПЛАЧЕНО" (or start of file) up to the following "СЧЕТ ВЫСТАВЛЕН" entry.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import re
from typing import List, Tuple, Optional


PAID = "ОПЛАЧЕНО"
INVOICED = "СЧЕТ ВЫСТАВЛЕН"

DATE_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")
TIME_PATTERN = re.compile(r"\d{1,2}:\d{2}")


def compute_interval(lines: List[str]) -> Tuple[float, Optional[str], Optional[str]]:
    """Return total minutes and the first/last date for the given log lines."""

    total_minutes = 0.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current_date: Optional[str] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if DATE_PATTERN.match(line):
            current_date = line
            if start_date is None:
                start_date = current_date
            end_date = current_date
            i += 1
            continue

        if TIME_PATTERN.match(line):
            block_times: List[str] = []
            while i < len(lines) and lines[i] and not DATE_PATTERN.match(lines[i]):
                block_times.extend(TIME_PATTERN.findall(lines[i]))
                i += 1

            if len(block_times) >= 2:
                t1 = datetime.strptime(block_times[0], "%H:%M")
                t2 = datetime.strptime(block_times[-1], "%H:%M")
                delta = (t2 - t1).total_seconds() / 60
                if delta < 0:
                    delta += 24 * 60
                total_minutes += delta
            continue

        i += 1

    return total_minutes, start_date, end_date


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Count working time blocks")
    parser.add_argument("logfile", help="Path to the log file")
    args = parser.parse_args(argv)

    with open(args.logfile, encoding="utf-8", newline="") as fh:
        raw_lines = fh.readlines()

    lines = [line.strip() for line in raw_lines]

    newline = "\r\n" if raw_lines and raw_lines[0].endswith("\r\n") else "\n"
    log_changed = False

    paid_indexes = [i for i, line in enumerate(lines) if PAID in line]
    last_paid_index = paid_indexes[-1] if paid_indexes else -1

    post_paid_lines = lines[last_paid_index + 1 :]
    total_minutes, start_date, end_date = compute_interval(post_paid_lines)

    # Find the first invoice after the last paid marker
    next_invoice_index = None
    for idx in range(last_paid_index + 1, len(lines)):
        if INVOICED in lines[idx]:
            next_invoice_index = idx
            break

    invoiced_minutes = None
    invoiced_end_date = None
    if next_invoice_index is not None:
        invoiced_lines = lines[last_paid_index + 1 : next_invoice_index]
        invoiced_minutes, _, invoiced_end_date = compute_interval(invoiced_lines)

    total_hours = round(total_minutes / 30) / 2
    print(f"{total_hours} часов (с {start_date} по {end_date})")

    if invoiced_minutes is not None:
        invoiced_hours = round(invoiced_minutes / 30) / 2
        print(
            f"{invoiced_hours} часов до {INVOICED} (с {start_date} по {invoiced_end_date})"
        )

        confirm = input("Mark this invoiced period as paid? [y/N] ").strip().lower()
        if confirm.startswith("y") and next_invoice_index is not None:
            raw_lines[next_invoice_index] = raw_lines[next_invoice_index].replace(INVOICED, PAID)
            print("Marked as paid.")
            log_changed = True

    # Compute not yet invoiced time (after the last invoice if present)
    unissued_start = next_invoice_index if next_invoice_index is not None else last_paid_index
    unissued_lines = lines[unissued_start + 1 :]
    unissued_minutes, unissued_start_date, unissued_end_date = compute_interval(unissued_lines)

    if unissued_minutes:
        unissued_hours = round(unissued_minutes / 30) / 2
        print(
            f"{unissued_hours} часов без {INVOICED} (с {unissued_start_date} по {unissued_end_date})"
        )
        confirm = input("Mark this period as invoiced? [y/N] ").strip().lower()
        if confirm.startswith("y"):
            trailing = 0
            while raw_lines and raw_lines[-1].strip() == "":
                raw_lines.pop()
                trailing += 1
            raw_lines.append(INVOICED + newline)
            raw_lines.extend([newline] * trailing)
            print("Marked as invoiced.")
            log_changed = True

    add = input("Add more log lines? [y/N] ").strip().lower()
    if add.startswith("y"):
        print("Enter log lines. Submit an empty line to finish:")
        while True:
            entry = input()
            if entry == "":
                break
            raw_lines.append(entry + newline)
        log_changed = True

    if log_changed:
        with open(args.logfile, "w", encoding="utf-8", newline="") as fh:
            fh.writelines(raw_lines)
        print("Log updated.")


if __name__ == "__main__":
    main()

