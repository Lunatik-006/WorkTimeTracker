import tkinter as tk
from tkinter import ttk
from time_entry import TimeEntry


class ActivityDialog(tk.Toplevel):
    """Dialog for editing or creating a single activity."""

    def __init__(self, parent, activity=None):
        super().__init__(parent)
        self.title("Activity")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text="Name").grid(row=0, column=0, sticky="w")
        self.entry_name = ttk.Entry(self)
        self.entry_name.grid(row=1, column=0, padx=5, sticky="we")

        ttk.Label(self, text="Duration").grid(row=2, column=0, sticky="w")
        self.time_entry = TimeEntry(self)
        self.time_entry.grid(row=3, column=0, padx=5, sticky="we")

        btn = ttk.Frame(self)
        btn.grid(row=4, column=0, pady=5, sticky="e")
        ttk.Button(btn, text="OK", command=self._ok).grid(row=0, column=0, padx=2)
        ttk.Button(btn, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=2)

        if activity:
            # Pre-fill fields when editing an existing activity
            self.entry_name.insert(0, activity.name)
            self.time_entry.set_seconds(activity.duration)

        self.columnconfigure(0, weight=1)

    def _ok(self):
        """Validate input and close the dialog with result."""
        name = self.entry_name.get().strip()
        if not name:
            return
        duration = self.time_entry.get_seconds()
        if duration <= 0:
            return
        self.result = (name, duration)
        self.destroy()
