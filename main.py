import tkinter as tk
from tkinter import ttk, messagebox
from timer_manager import TimerManager
from timer_editor import TimerEditorFrame
from timer_runner import TimerRunner


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Timer")
        self.geometry("700x550")
        self.manager = TimerManager()
        self.editor = TimerEditorFrame(self, self.manager, self.on_editor_closed)
        self.create_widgets()

    def on_editor_closed(self):
        self.manager.load_timers()
        self.refresh_timer_list()

    def create_widgets(self):
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left, text="Timers").pack(anchor="w")
        columns = ("edit", "run", "delete")
        self.timer_list = ttk.Treeview(left, columns=columns, show="tree")
        self.timer_list.column("#0", stretch=True)
        for col in columns:
            self.timer_list.column(col, width=30, anchor="center", stretch=False)
        self.timer_list.pack(fill=tk.BOTH, expand=True)
        self.timer_list.bind("<Double-1>", self.on_double_click)
        self.timer_list.bind("<Button-1>", self.on_click)
        self.timer_list.bind("<Delete>", self.on_delete_key)
        self.refresh_timer_list()

        ttk.Button(left, text="+ New Timer", command=self.new_timer).pack(pady=5, fill=tk.X)

        self.editor.pack_forget()

    def refresh_timer_list(self):
        self.timer_list.delete(*self.timer_list.get_children())
        for name in sorted(self.manager.timers.keys()):
            self.timer_list.insert("", tk.END, iid=name, text=name, values=("✏", "▶", "🗑"))

    def get_selected_name(self):
        sel = self.timer_list.selection()
        if not sel:
            return None
        return sel[0]

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
        if messagebox.askokcancel("Delete", f"Вы действительно хотите удалить таймер '{name}'?"):
            self.manager.delete_timer(name)
            self.refresh_timer_list()

    def run_timer(self):
        name = self.get_selected_name()
        if not name:
            return
        timer = self.manager.timers[name]
        TimerRunner(self, timer)

    def on_double_click(self, event):
        item = self.timer_list.identify_row(event.y)
        if item:
            self.timer_list.selection_set(item)
            self.edit_timer()

    def on_click(self, event):
        item = self.timer_list.identify_row(event.y)
        col = self.timer_list.identify_column(event.x)
        if not item or col == "#0":
            return
        self.timer_list.selection_set(item)
        if col == "#1":
            self.edit_timer()
        elif col == "#2":
            self.run_timer()
        elif col == "#3":
            self.delete_timer()

    def on_delete_key(self, event):
        self.delete_timer()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
