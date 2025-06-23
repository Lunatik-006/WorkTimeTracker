from __future__ import annotations
import os
from datetime import datetime
from typing import List, Tuple, Optional

from .constants import PAID, INVOICED, DATE_PATTERN, TIME_PATTERN


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
        pending: List[dict] = []
        current_date = None
        start_time: Optional[str] = None
        end_time: Optional[str] = None
        start_idx = 0
        for idx, line in enumerate(lines):
            if DATE_PATTERN.match(line):
                if start_time is not None:
                    pending.append({
                        "date": current_date,
                        "start": start_time,
                        "end": end_time,
                        "start_idx": start_idx,
                        "end_idx": idx - 1,
                    })
                    start_time = end_time = None
                current_date = line
                start_idx = idx
            elif PAID in line or INVOICED in line:
                if start_time is not None:
                    pending.append({
                        "date": current_date,
                        "start": start_time,
                        "end": end_time,
                        "start_idx": start_idx,
                        "end_idx": idx - 1,
                    })
                    start_time = end_time = None
                status = line.strip()
                for item in pending:
                    item["status"] = status
                    intervals.append(item)
                pending = []
                current_date = None
            elif not line.strip():
                if start_time is not None:
                    pending.append({
                        "date": current_date,
                        "start": start_time,
                        "end": end_time,
                        "start_idx": start_idx,
                        "end_idx": idx - 1,
                        "rest_after": True,
                    })
                    start_time = end_time = None
                continue
            elif TIME_PATTERN.search(line):
                times = TIME_PATTERN.findall(line)
                if start_time is None:
                    start_time = times[0]
                    start_idx = idx
                end_time = times[-1]
        if start_time is not None:
            pending.append({
                "date": current_date,
                "start": start_time,
                "end": end_time,
                "start_idx": start_idx,
                "end_idx": len(lines) - 1,
            })
        intervals.extend(pending)
        return intervals

    def intervals_with_statuses(self) -> List[str]:
        intervals = self.parse_intervals()
        result = []
        for idx, item in enumerate(intervals):
            if "start" not in item:
                continue
            status_line = item.get("status")
            if status_line:
                st = "PAID" if PAID in status_line else "INVOICED" if INVOICED in status_line else "UNPAID"
            else:
                st = "UNPAID"
            result.append(f"{item['date']} {item['start']} - {item['end']} {st}")
            if item.get("rest_after"):
                next_item = intervals[idx + 1] if idx + 1 < len(intervals) else None
                if next_item and next_item.get("date") == item.get("date"):
                    result.append("------------")
        return result

    def parse_periods(self) -> List[dict]:
        periods: List[dict] = []
        current_period: dict = {"dates": [], "status": None}
        current_date: Optional[str] = None
        notes: List[str] = []
        for line in self.lines:
            if PAID in line or INVOICED in line:
                if current_date is not None:
                    current_period["dates"].append({"date": current_date, "notes": notes})
                    current_date = None
                    notes = []
                current_period["status"] = line.strip()
                if current_period["dates"] or current_period["status"]:
                    current_period["start"] = current_period["dates"][0]["date"] if current_period["dates"] else ""
                    current_period["end"] = current_period["dates"][-1]["date"] if current_period["dates"] else ""
                    periods.append(current_period)
                current_period = {"dates": [], "status": None}
            elif DATE_PATTERN.match(line):
                if current_date is not None:
                    current_period["dates"].append({"date": current_date, "notes": notes})
                current_date = line
                notes = []
            else:
                notes.append(line)
        if current_date is not None:
            current_period["dates"].append({"date": current_date, "notes": notes})
        if current_period["dates"] or current_period.get("status"):
            current_period["start"] = current_period["dates"][0]["date"] if current_period["dates"] else ""
            current_period["end"] = current_period["dates"][-1]["date"] if current_period["dates"] else ""
            periods.append(current_period)
        return periods

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
