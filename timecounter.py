"""Simple CLI tool for counting working time blocks in a log file.

The script sums time intervals between the first and last timestamp of each
block after the most recent "ОПЛАЧЕНО" status.  It also calculates the amount of
time already invoiced but not yet paid - the interval from the last
"ОПЛАЧЕНО" (or start of file) up to the following "СЧЕТ ВЫСТАВЛЕН" entry.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime
import re
from typing import List, Tuple, Optional


PAID = "ОПЛАЧЕНО"
INVOICED = "СЧЕТ ВЫСТАВЛЕН"

DATE_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")
TIME_PATTERN = re.compile(r"\d{1,2}:\d{2}")

class TimeCounter:
    """Represents a time log and provides operations on it."""

    def __init__(self, logfile: str) -> None:
        self.logfile = logfile
        self.newline = "\n"
        self.lines: List[str] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.logfile):
            self.lines = []
            return
        with open(self.logfile, encoding="utf-8", newline="") as fh:
            raw = fh.readlines()
        self.newline = "\r\n" if raw and raw[0].endswith("\r\n") else "\n"
        self.lines = [line.strip() for line in raw]

    def save(self) -> None:
        with open(self.logfile, "w", encoding="utf-8", newline="") as fh:
            fh.write(self.newline.join(self.lines))

    @staticmethod
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

    def parse_intervals(self) -> List[dict]:
        lines = self.lines
        intervals = []
        current_date = None
        times: List[str] = []
        start_idx = 0
        for idx, line in enumerate(lines):
            if DATE_PATTERN.match(line):
                if times:
                    intervals.append(
                        {
                            "date": current_date,
                            "start": times[0],
                            "end": times[-1],
                            "start_idx": start_idx,
                            "end_idx": idx - 1,
                        }
                    )
                    times = []
                current_date = line
                start_idx = idx
            elif TIME_PATTERN.search(line):
                times.extend(TIME_PATTERN.findall(line))
            elif PAID in line or INVOICED in line:
                if times:
                    intervals.append(
                        {
                            "date": current_date,
                            "start": times[0],
                            "end": times[-1],
                            "start_idx": start_idx,
                            "end_idx": idx - 1,
                        }
                    )
                    times = []
                intervals.append({"status": line.strip(), "idx": idx})
        if times:
            intervals.append(
                {
                    "date": current_date,
                    "start": times[0],
                    "end": times[-1],
                    "start_idx": start_idx,
                    "end_idx": len(lines) - 1,
                }
            )
        return intervals

    def intervals_with_statuses(self) -> List[str]:
        intervals = self.parse_intervals()
        paid_indexes = [i for i, line in enumerate(self.lines) if PAID in line]
        last_paid = paid_indexes[-1] if paid_indexes else -1
        invoice_index = None
        for idx in range(last_paid + 1, len(self.lines)):
            if INVOICED in self.lines[idx]:
                invoice_index = idx
                break
        result = []
        for item in intervals:
            if "status" in item:
                continue
            if item["end_idx"] <= last_paid:
                st = "PAID"
            elif invoice_index is not None and item["start_idx"] < invoice_index:
                st = "INVOICED"
            else:
                st = "UNPAID"
            result.append(f"{item['date']} {item['start']} - {item['end']} {st}")
        return result

    def compute_totals(self) -> str:
        paid_indexes = [i for i, line in enumerate(self.lines) if PAID in line]
        last_paid_index = paid_indexes[-1] if paid_indexes else -1
        post_paid = self.lines[last_paid_index + 1 :]
        total_minutes, start_date, end_date = self.compute_interval(post_paid)
        next_invoice_index = None
        for idx in range(last_paid_index + 1, len(self.lines)):
            if INVOICED in self.lines[idx]:
                next_invoice_index = idx
                break
        invoiced_minutes = None
        invoiced_end_date = None
        if next_invoice_index is not None:
            invoiced_lines = self.lines[last_paid_index + 1 : next_invoice_index]
            invoiced_minutes, _, invoiced_end_date = self.compute_interval(invoiced_lines)
        unissued_start = next_invoice_index if next_invoice_index is not None else last_paid_index
        unissued_lines = self.lines[unissued_start + 1 :]
        unissued_minutes, unissued_start_date, unissued_end_date = self.compute_interval(unissued_lines)
        res = []
        if total_minutes:
            res.append(f"{round(total_minutes / 30) / 2} часов (с {start_date} по {end_date})")
        if invoiced_minutes is not None:
            res.append(
                f"{round(invoiced_minutes / 30) / 2} часов до {INVOICED} (с {start_date} по {invoiced_end_date})"
            )
        if unissued_minutes:
            res.append(
                f"{round(unissued_minutes / 30) / 2} часов без {INVOICED} (с {unissued_start_date} по {unissued_end_date})"
            )
        return "\n".join(res)

    def mark_invoice_as_paid(self) -> bool:
        paid_indexes = [i for i, line in enumerate(self.lines) if PAID in line]
        last_paid_index = paid_indexes[-1] if paid_indexes else -1
        next_invoice_index = None
        for idx in range(last_paid_index + 1, len(self.lines)):
            if INVOICED in self.lines[idx]:
                next_invoice_index = idx
                break
        if next_invoice_index is not None:
            self.lines[next_invoice_index] = self.lines[next_invoice_index].replace(INVOICED, PAID)
            self.save()
            return True
        return False

    def mark_last_period_as_invoiced(self) -> bool:
        paid_indexes = [i for i, line in enumerate(self.lines) if PAID in line]
        last_paid_index = paid_indexes[-1] if paid_indexes else -1
        for idx in range(last_paid_index + 1, len(self.lines)):
            if INVOICED in self.lines[idx]:
                return False
        self.lines.append(INVOICED)
        self.save()
        return True

    def add_entry(self, date: str, start: str, end: str, note: str) -> None:
        if not self.lines or self.lines[-1] != date:
            self.lines.extend([date, ""])
        self.lines.append(f"{start} {note}".strip())
        self.lines.append(end)
        self.save()


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Count working time blocks")
    parser.add_argument("logfile", help="Path to the log file")
    args = parser.parse_args(argv)

    tc = TimeCounter(args.logfile)

    print(tc.compute_totals())

    if tc.mark_invoice_as_paid():
        print("Marked invoice as paid.")

    add = input("Add more log lines? [y/N] ").strip().lower()
    if add.startswith("y"):
        print("Enter log lines. Submit an empty line to finish:")
        while True:
            entry = input()
            if entry == "":
                break
            tc.lines.append(entry)
        tc.save()


if __name__ == "__main__":
    main()

