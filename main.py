import tkinter as tk
from tkinter import ttk, messagebox
from timer_manager import TimerManager
from timer_editor import TimerEditorFrame
from timer_runner import TimerRunner


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


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
