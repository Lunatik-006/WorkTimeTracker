import tkinter as tk
from tkinter import ttk


class TimeEntry(ttk.Entry):
    """Entry widget for time in HH:MM:SS format with digit based editing."""

    def __init__(self, master, seconds=0, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.set_seconds(seconds)
        self.bind("<FocusOut>", self._on_done)
        self.bind("<Return>", self._on_done)

    def _on_done(self, event=None):
        digits = "".join(ch for ch in self.var.get() if ch.isdigit())
        if not digits:
            self.var.set("00:00:00")
            return
        sec = int(digits[-2:]) if len(digits) >= 2 else int(digits)
        sec = min(sec, 59)
        minute_digits = digits[-4:-2] if len(digits) > 2 else ""
        minutes = int(minute_digits) if minute_digits else 0
        minutes = min(minutes, 59)
        hour_digits = digits[:-4] if len(digits) > 4 else ""
        hours = int(hour_digits) if hour_digits else 0
        self.var.set(f"{hours:02d}:{minutes:02d}:{sec:02d}")
        self.icursor(tk.END)
        return "break" if event and event.keysym == "Return" else None

    def get_seconds(self) -> int:
        text = self.var.get()
        if ":" not in text:
            digits = "".join(ch for ch in text if ch.isdigit())
            if not digits:
                return 0
            sec = int(digits[-2:]) if len(digits) >= 2 else int(digits)
            sec = min(sec, 59)
            minute_digits = digits[-4:-2] if len(digits) > 2 else ""
            minutes = int(minute_digits) if minute_digits else 0
            minutes = min(minutes, 59)
            hour_digits = digits[:-4] if len(digits) > 4 else ""
            hours = int(hour_digits) if hour_digits else 0
        else:
            try:
                hours, minutes, sec = [int(x) for x in text.split(":")]
            except ValueError:
                return 0
            minutes = min(minutes, 59)
            sec = min(sec, 59)
        return hours * 3600 + minutes * 60 + sec

    def set_seconds(self, sec: int):
        h, rem = divmod(int(sec), 3600)
        m, s = divmod(rem, 60)
        self.var.set(f"{h:02d}:{m:02d}:{s:02d}")
