import tkinter as tk
from tkinter import ttk
from models import Activity, TimerConfig
from activity_dialog import ActivityDialog
from time_entry import TimeEntry


class TimerEditorFrame(ttk.Frame):
    """Editing UI placed inside the main application window."""

    def __init__(self, parent, manager, close_callback):
        super().__init__(parent)
        self.manager = manager
        self.close_callback = close_callback
        self.timer = None
        self._build_widgets()
        self.grid_columnconfigure(0, weight=1)

    def _build_widgets(self):
        ttk.Label(self, text="Name").grid(row=0, column=0, sticky="w")
        self.entry_name = ttk.Entry(self)
        self.entry_name.grid(row=1, column=0, sticky="we", pady=(0, 5))

        ttk.Label(self, text="Description").grid(row=2, column=0, sticky="w")
        self.text_desc = tk.Text(self, height=3, width=30)
        self.text_desc.grid(row=3, column=0, sticky="we", pady=(0, 5))

        ttk.Label(self, text="Sets").grid(row=4, column=0, sticky="w")
        self.spin_sets = ttk.Spinbox(self, from_=1, to=20, width=5)
        self.spin_sets.grid(row=5, column=0, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Rest between activities").grid(row=6, column=0, sticky="w")
        self.time_rest_act = TimeEntry(self)
        self.time_rest_act.grid(row=7, column=0, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Rest between sets").grid(row=8, column=0, sticky="w")
        self.time_rest_set = TimeEntry(self)
        self.time_rest_set.grid(row=9, column=0, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Activities").grid(row=10, column=0, sticky="w")
        self.listbox = tk.Listbox(self, height=8)
        self.listbox.grid(row=11, column=0, sticky="we")
        self.listbox.bind('<Button-1>', self.set_drag_start)
        self.listbox.bind('<B1-Motion>', self.drag_motion)
        self.drag_index = None

        act_btns = ttk.Frame(self)
        act_btns.grid(row=12, column=0, sticky="w")
        ttk.Button(act_btns, text="Add", command=self.add_activity).grid(row=0, column=0, padx=2)
        ttk.Button(act_btns, text="Edit", command=self.edit_activity).grid(row=0, column=1, padx=2)
        ttk.Button(act_btns, text="Delete", command=self.delete_activity).grid(row=0, column=2, padx=2)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=13, column=0, sticky="e", pady=5)
        ttk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=1, padx=2)

    def edit_timer(self, timer=None):
        self.timer = timer or TimerConfig("New Timer")
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, self.timer.name)
        self.text_desc.delete("1.0", tk.END)
        self.text_desc.insert("1.0", self.timer.description)
        self.spin_sets.delete(0, tk.END)
        self.spin_sets.insert(0, str(self.timer.sets))
        self.time_rest_act.set_seconds(self.timer.rest_activity)
        self.time_rest_set.set_seconds(self.timer.rest_set)
        self.refresh_listbox()
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def cancel(self):
        self.pack_forget()
        if self.close_callback:
            self.close_callback()

    def set_drag_start(self, event):
        self.drag_index = self.listbox.nearest(event.y)

    def drag_motion(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_index:
            self.timer.activities.insert(new_index, self.timer.activities.pop(self.drag_index))
            self.refresh_listbox()
            self.drag_index = new_index

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for act in self.timer.activities:
            self.listbox.insert(tk.END, f"{act.name} ({self.format_time(act.duration)})")

    def format_time(self, sec):
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def add_activity(self):
        dlg = ActivityDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            name, duration = dlg.result
            self.timer.activities.append(Activity(name, duration))
            self.refresh_listbox()

    def edit_activity(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        act = self.timer.activities[idx]
        dlg = ActivityDialog(self, act)
        self.wait_window(dlg)
        if dlg.result:
            name, duration = dlg.result
            act.name = name
            act.duration = duration
            self.refresh_listbox()

    def delete_activity(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return
        del self.timer.activities[idxs[0]]
        self.refresh_listbox()

    def save(self):
        self.timer.name = self.entry_name.get().strip()
        self.timer.description = self.text_desc.get("1.0", "end").strip()
        self.timer.sets = int(self.spin_sets.get())
        self.timer.rest_activity = self.time_rest_act.get_seconds()
        self.timer.rest_set = self.time_rest_set.get_seconds()
        self.manager.save_timer(self.timer)
        self.cancel()
