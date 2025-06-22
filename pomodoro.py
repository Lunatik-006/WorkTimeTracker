# Pomodoro timer application using Tkinter

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

CONFIG_DIR = "timers"

class Activity:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration  # seconds

    def to_dict(self):
        return {"name": self.name, "duration": self.duration}

    @staticmethod
    def from_dict(data):
        return Activity(data["name"], data["duration"])

class TimerConfig:
    def __init__(self, name: str, description: str = "", sets: int = 1,
                 rest_activity: int = 5*60, rest_set: int = 15*60):
        self.name = name
        self.description = description
        self.activities = []  # list of Activity
        self.sets = sets
        self.rest_activity = rest_activity
        self.rest_set = rest_set

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "sets": self.sets,
            "rest_activity": self.rest_activity,
            "rest_set": self.rest_set,
            "activities": [a.to_dict() for a in self.activities],
        }

    @staticmethod
    def from_dict(data):
        cfg = TimerConfig(data["name"], data.get("description", ""),
                          data.get("sets", 1), data.get("rest_activity", 300),
                          data.get("rest_set", 900))
        cfg.activities = [Activity.from_dict(a) for a in data.get("activities", [])]
        return cfg

class TimerManager:
    def __init__(self, directory=CONFIG_DIR):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self.timers = {}
        self.load_timers()

    def _path(self, name):
        filename = f"{name}.json"
        return os.path.join(self.directory, filename)

    def load_timers(self):
        self.timers = {}
        for fn in os.listdir(self.directory):
            if fn.endswith('.json'):
                with open(os.path.join(self.directory, fn), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cfg = TimerConfig.from_dict(data)
                    self.timers[cfg.name] = cfg

    def save_timer(self, timer: TimerConfig):
        with open(self._path(timer.name), 'w', encoding='utf-8') as f:
            json.dump(timer.to_dict(), f, indent=2)
        self.timers[timer.name] = timer

    def delete_timer(self, name):
        if name in self.timers:
            path = self._path(name)
            if os.path.exists(path):
                os.remove(path)
            del self.timers[name]

    def rename_timer(self, old_name, new_name):
        if old_name == new_name:
            return
        timer = self.timers.pop(old_name)
        timer.name = new_name
        old_path = self._path(old_name)
        new_path = self._path(new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        self.save_timer(timer)


class TimeEntry(ttk.Entry):
    """Entry widget for time in HH:MM:SS format with digit based editing."""

    def __init__(self, master, seconds=0, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.set_seconds(seconds)
        self.bind("<KeyRelease>", self._on_key)

    def _on_key(self, event):
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

    def get_seconds(self):
        try:
            h, m, s = [int(x) for x in self.var.get().split(":")]
        except ValueError:
            return 0
        m = min(m, 59)
        s = min(s, 59)
        return h * 3600 + m * 60 + s

    def set_seconds(self, sec):
        h, rem = divmod(int(sec), 3600)
        m, s = divmod(rem, 60)
        self.var.set(f"{h:02d}:{m:02d}:{s:02d}")


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
            self.entry_name.insert(0, activity.name)
            self.time_entry.set_seconds(activity.duration)

        self.columnconfigure(0, weight=1)

    def _ok(self):
        name = self.entry_name.get().strip()
        if not name:
            return
        duration = self.time_entry.get_seconds()
        if duration <= 0:
            return
        self.result = (name, duration)
        self.destroy()


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

class TimerRunner:
    def __init__(self, parent, timer: TimerConfig):
        self.parent = parent
        self.timer = timer
        self.current_set = 1
        self.current_index = 0
        self.remaining = 0
        self.running = False
        self.paused = False
        self.timer_id = None

        self.window = tk.Toplevel(parent)
        self.window.title(f"Timer: {timer.name}")

        self.label_activity = ttk.Label(self.window, text="")
        self.label_activity.pack(pady=5)

        self.label_time = ttk.Label(self.window, text="00:00", font=("Arial", 24))
        self.label_time.pack(pady=5)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack()

        self.btn_start = ttk.Button(btn_frame, text="Start", command=self.start)
        self.btn_start.grid(row=0, column=0, padx=2)
        self.btn_pause = ttk.Button(btn_frame, text="Pause", command=self.pause)
        self.btn_pause.grid(row=0, column=1, padx=2)
        self.btn_stop = ttk.Button(btn_frame, text="Stop", command=self.stop)
        self.btn_stop.grid(row=0, column=2, padx=2)
        self.btn_next = ttk.Button(btn_frame, text="Next", command=self.next_activity)
        self.btn_next.grid(row=0, column=3, padx=2)

        self.update_display()

    def format_time(self, seconds):
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_display(self):
        if self.current_index < len(self.timer.activities):
            act = self.timer.activities[self.current_index]
            self.label_activity.config(text=f"Set {self.current_set}/{self.timer.sets}: {act.name}")
        else:
            self.label_activity.config(text="Rest between sets")
        self.label_time.config(text=self.format_time(self.remaining))

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            if self.remaining == 0:
                self.start_current_activity()
            self.tick()

    def start_current_activity(self):
        if self.current_index < len(self.timer.activities):
            self.remaining = self.timer.activities[self.current_index].duration
        else:
            self.remaining = self.timer.rest_set
        self.update_display()

    def pause(self):
        if self.running:
            self.paused = not self.paused
            if not self.paused:
                self.tick()

    def stop(self):
        if self.running:
            if self.timer_id:
                self.window.after_cancel(self.timer_id)
            self.running = False
        self.current_set = 1
        self.current_index = 0
        self.remaining = 0
        self.update_display()

    def next_activity(self):
        if self.running:
            if self.timer_id:
                self.window.after_cancel(self.timer_id)
        self.advance()

    def advance(self):
        if self.current_index < len(self.timer.activities):
            self.current_index += 1
            if self.current_index < len(self.timer.activities):
                self.remaining = self.timer.rest_activity
                self.label_activity.config(text="Rest")
                self.tick()
            else:
                self.remaining = self.timer.rest_set
                self.label_activity.config(text="Rest between sets")
                self.tick()
        else:
            self.current_set += 1
            if self.current_set > self.timer.sets:
                messagebox.showinfo("Timer", "All sets completed")
                self.stop()
                return
            self.current_index = 0
            self.start_current_activity()
            if self.running:
                self.tick()

    def tick(self):
        if not self.running or self.paused:
            return
        if self.remaining > 0:
            self.label_time.config(text=self.format_time(self.remaining))
            self.remaining -= 1
            self.timer_id = self.window.after(1000, self.tick)
        else:
            self.advance()


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Timer")
        self.geometry("700x400")
        self.manager = TimerManager()
        self.editor = TimerEditorFrame(self, self.manager, self.on_editor_closed)
        self.create_widgets()

    def on_editor_closed(self):
        self.manager.load_timers()
        self.refresh_timer_list()

    def create_widgets(self):
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left, text="Timers").pack()
        self.timer_list = tk.Listbox(left, height=20)
        self.timer_list.pack(fill=tk.BOTH, expand=True)
        self.refresh_timer_list()

        btn_frame = ttk.Frame(left)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="New", command=self.new_timer).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_timer).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_timer).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Run", command=self.run_timer).grid(row=0, column=3, padx=2)

        self.editor.pack_forget()

    def refresh_timer_list(self):
        self.timer_list.delete(0, tk.END)
        for name in sorted(self.manager.timers.keys()):
            self.timer_list.insert(tk.END, name)

    def get_selected_name(self):
        sel = self.timer_list.curselection()
        if not sel:
            return None
        return self.timer_list.get(sel[0])

    def new_timer(self):
        self.editor.edit_timer()

    def edit_timer(self):
        name = self.get_selected_name()
        if not name:
            return
        timer = self.manager.timers[name]
        self.editor.edit_timer(timer)

    def delete_timer(self):
        name = self.get_selected_name()
        if not name:
            return
        if messagebox.askyesno("Delete", f"Delete timer '{name}'?"):
            self.manager.delete_timer(name)
            self.refresh_timer_list()

    def run_timer(self):
        name = self.get_selected_name()
        if not name:
            return
        timer = self.manager.timers[name]
        TimerRunner(self, timer)

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
