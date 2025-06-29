import tkinter as tk
from tkinter import messagebox, ttk

from models import TimerConfig
from tts import speak


class TimerRunner:
    """Window that runs a configured timer."""

    def __init__(self, parent, timer: TimerConfig):
        """Create a new top level window for running *timer*."""
        self.parent = parent
        self.timer = timer
        self.current_set = 1
        self.current_index = 0
        self.remaining = 0
        self.running = False
        self.paused = False
        self.timer_id = None
        self.state = "activity"  # activity, rest_activity, rest_set

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

    def _popup(self):
        """Show the window in the center of the screen above others."""
        self.window.deiconify()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        self.window.after(1000, lambda: self.window.attributes("-topmost", False))

    def format_time(self, seconds):
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_display(self):
        """Refresh labels based on current state and remaining time."""
        if self.state == "activity" and self.current_index < len(self.timer.activities):
            act = self.timer.activities[self.current_index]
            self.label_activity.config(
                text=f"Set {self.current_set}/{self.timer.sets}: {act.name}"
            )
        elif self.state == "rest_activity":
            self.label_activity.config(text="Rest")
        else:
            self.label_activity.config(text="Rest between sets")
        self.label_time.config(text=self.format_time(self.remaining))

    def start(self):
        """Begin or resume timer execution."""
        if not self.running:
            self.running = True
            self.paused = False
            if self.remaining == 0:
                self.start_current_activity()
            speak("таймер запущен")
            self.tick()

    def start_current_activity(self):
        """Switch state to the current activity and announce it."""
        self.state = "activity"
        act = self.timer.activities[self.current_index]
        self.remaining = act.duration
        self.update_display()
        speak(act.name)

    def pause(self):
        """Toggle paused state."""
        if self.running:
            self.paused = not self.paused
            if not self.paused:
                self.tick()

    def stop(self):
        """Reset timer to its initial state."""
        if self.running and self.timer_id:
            self.window.after_cancel(self.timer_id)
        self.running = False
        self.current_set = 1
        self.current_index = 0
        self.remaining = 0
        self.state = "activity"
        self.update_display()
        speak("таймер остановлен")

    def next_activity(self):
        """Skip to the next timer phase."""
        if self.running and self.timer_id:
            self.window.after_cancel(self.timer_id)
        self.advance()

    def advance(self, auto=False):
        """Move to the next logical phase of the timer."""
        if self.state == "activity":
            if self.current_index < len(self.timer.activities) - 1:
                self.state = "rest_activity"
                self.remaining = self.timer.rest_activity
            else:
                self.state = "rest_set"
                self.remaining = self.timer.rest_set
            speak("отдых")
            self.update_display()
            if auto and self.window.state() != "normal":
                self._popup()
            self.tick()
        elif self.state == "rest_activity":
            self.current_index += 1
            self.start_current_activity()
            if auto and self.window.state() != "normal":
                self._popup()
            if self.running:
                self.tick()
        else:  # rest_set
            self.current_set += 1
            if self.current_set > self.timer.sets:
                messagebox.showinfo("Timer", "All sets completed")
                self.stop()
                return
            self.current_index = 0
            self.start_current_activity()
            if auto and self.window.state() != "normal":
                self._popup()
            if self.running:
                self.tick()

    def tick(self):
        """One second timer callback handling countdown."""
        if not self.running or self.paused:
            return
        if self.remaining > 0:
            self.label_time.config(text=self.format_time(self.remaining))
            self.remaining -= 1
            self.timer_id = self.window.after(1000, self.tick)
        else:
            self.advance(auto=True)
