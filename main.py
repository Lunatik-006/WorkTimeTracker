import tkinter as tk
from tkinter import ttk, messagebox
from timer_manager import TimerManager
from timer_editor import TimerEditorFrame
from timer_runner import TimerRunner


class MainApp(tk.Tk):
    """Main window with the list of timers and editor frame."""

    def __init__(self):
        super().__init__()
        # When started we show the list of saved timers. The editor is hidden
        # until the user creates or edits a timer.
        self.title("Pomodoro Timer")
        # Geometry for compact view and when the editor is visible
        self.normal_geometry = "260x500"
        self.editor_geometry = "620x500"
        self.geometry(self.normal_geometry)
        # TimerManager loads configurations from disk
        self.manager = TimerManager()
        # Editor frame is created once and shown/hidden as needed
        self.editor = TimerEditorFrame(self, self.manager, self.on_editor_closed)
        self.create_widgets()

    def on_editor_closed(self):
        """Reload timers after the editor window is closed."""
        self.manager.load_timers()
        self.refresh_timer_list()
        self.geometry(self.normal_geometry)

    def create_widgets(self):
        """Build the list of timers and control buttons."""

        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left, text="Timers").pack(anchor="w")
        columns = ("edit", "run", "delete")  # icons for actions
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
        """Populate the tree widget with available timers."""
        self.timer_list.delete(*self.timer_list.get_children())
        for name in sorted(self.manager.timers.keys()):
            self.timer_list.insert("", tk.END, iid=name, text=name, values=("✏", "▶", "🗑"))

    def get_selected_name(self):
        sel = self.timer_list.selection()
        if not sel:
            return None
        return sel[0]

    def new_timer(self):
        """Open the editor to create a new timer."""
        self.editor.edit_timer()
        self.geometry(self.editor_geometry)

    def edit_timer(self):
        """Edit the currently selected timer."""
        name = self.get_selected_name()
        if not name:
            return
        timer = self.manager.timers[name]
        self.editor.edit_timer(timer)
        self.geometry(self.editor_geometry)

    def delete_timer(self):
        """Delete the selected timer after confirmation."""
        name = self.get_selected_name()
        if not name:
            return
        if messagebox.askokcancel("Delete", f"Вы действительно хотите удалить таймер '{name}'?"):
            self.manager.delete_timer(name)
            self.refresh_timer_list()

    def run_timer(self):
        """Launch the timer runner window for the selection."""
        name = self.get_selected_name()
        if not name:
            return
        timer = self.manager.timers[name]
        TimerRunner(self, timer)

    def on_double_click(self, event):
        """Handle double click on a timer to open the editor."""
        item = self.timer_list.identify_row(event.y)
        if item:
            self.timer_list.selection_set(item)
            self.edit_timer()

    def on_click(self, event):
        """Handle clicks on action columns of the tree view."""
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
        """Keyboard shortcut for deleting a timer."""
        self.delete_timer()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
