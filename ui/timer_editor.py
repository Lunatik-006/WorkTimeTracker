import tkinter as tk
from tkinter import ttk, messagebox
import re
from core.models import Activity, TimerConfig
from ui.time_entry import TimeEntry


class TimerEditorFrame(ttk.Frame):
    """Editing UI placed inside the main application window."""

    def __init__(self, parent, manager, close_callback):
        super().__init__(parent)
        self.manager = manager
        # Function to call when the editor is closed
        self.close_callback = close_callback
        self.timer = None
        self.edit_item = None
        # Build all child widgets once during initialisation
        self._build_widgets()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _build_widgets(self):
        """Construct the form for editing timer properties."""
        ttk.Label(self, text="Name").grid(row=0, column=0, columnspan=2, sticky="w")
        self.entry_name = ttk.Entry(self, width=40)
        self.entry_name.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 5))

        ttk.Label(self, text="Description").grid(row=2, column=0, columnspan=2, sticky="w")
        self.text_desc = tk.Text(self, height=2, width=40, wrap="word")
        self.text_desc.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 5))

        ttk.Label(self, text="Sets").grid(row=4, column=0, columnspan=2, sticky="w")
        self.spin_sets = ttk.Spinbox(self, from_=1, to=99, width=5)
        self.spin_sets.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Rest between activities").grid(row=6, column=0, columnspan=2, sticky="w")
        self.time_rest_act = TimeEntry(self, width=8)
        self.time_rest_act.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Rest between sets").grid(row=8, column=0, columnspan=2, sticky="w")
        self.time_rest_set = TimeEntry(self, width=8)
        self.time_rest_set.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 5))

        ttk.Label(self, text="Activities").grid(row=10, column=0, columnspan=2, sticky="w")
        columns = ("time", "edit", "delete")
        self.tree = ttk.Treeview(self, columns=columns, show="tree", height=5)
        self.tree.grid(row=11, column=0, columnspan=2, sticky="nsew")
        self.tree.column("#0", stretch=True)
        self.tree.column("time", width=70, anchor="center", stretch=False)
        self.tree.column("edit", width=30, anchor="center", stretch=False)
        self.tree.column("delete", width=30, anchor="center", stretch=False)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double)
        self.tree.bind('<ButtonPress-1>', self.set_drag_start, add="+")
        self.tree.bind('<B1-Motion>', self.drag_motion, add="+")
        self.drag_index = None

        self.bind_all("<Button-1>", self._outside_click, add="+")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=12, column=1, sticky="e", pady=5)
        ttk.Button(btn_frame, text="Save", width=10, command=self.save).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Cancel", width=10, command=self.cancel).grid(row=0, column=1, padx=2)

    def edit_timer(self, timer=None):
        """Populate widgets with timer data and show the editor."""
        self.timer = timer or TimerConfig("New Timer")
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, self.timer.name)
        self.text_desc.delete("1.0", tk.END)
        self.text_desc.insert("1.0", self.timer.description)
        self.spin_sets.delete(0, tk.END)
        self.spin_sets.insert(0, str(self.timer.sets))
        self.time_rest_act.set_seconds(self.timer.rest_activity)
        self.time_rest_set.set_seconds(self.timer.rest_set)
        self.refresh_tree()
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def cancel(self):
        """Close the editor without saving changes."""
        self.finish_edit(False)
        self.pack_forget()
        if self.close_callback:
            self.close_callback()

    def set_drag_start(self, event):
        """Remember the index of the activity being dragged."""
        item = self.tree.identify_row(event.y)
        if item and item != "add":
            self.drag_index = self.tree.index(item)
        else:
            self.drag_index = None

    def drag_motion(self, event):
        """Handle drag-and-drop reordering inside the activity list."""
        item = self.tree.identify_row(event.y)
        if self.drag_index is None or not item or item == "add":
            return
        new_index = self.tree.index(item)
        if new_index != self.drag_index:
            self.timer.activities.insert(new_index, self.timer.activities.pop(self.drag_index))
            self.refresh_tree()
            self.drag_index = new_index

    def refresh_tree(self):
        """Refresh activity tree widget from the timer model."""
        self.tree.delete(*self.tree.get_children())
        for i, act in enumerate(self.timer.activities):
            self.tree.insert("", "end", iid=str(i), text=act.name,
                            values=(self.format_time(act.duration), "✏", "🗑"))
        self.tree.insert("", "end", iid="add", text="Add activity", values=("", "➕", ""))
        self.tree.config(height=min(len(self.timer.activities) + 1, 26))

    def format_time(self, sec):
        """Format seconds as HH:MM:SS string."""
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def add_activity(self):
        """Append a new default activity and start editing it."""
        if len(self.timer.activities) >= 25:
            messagebox.showwarning("Limit", "Maximum 25 activities per timer")
            return
        new = Activity("New", 60)
        self.timer.activities.append(new)
        self.refresh_tree()
        self.start_edit(str(len(self.timer.activities) - 1))

    def edit_activity(self, iid):
        """Begin editing the activity with the given tree id."""
        self.start_edit(iid)

    def delete_activity(self, iid):
        """Remove activity from the timer."""
        index = int(iid)
        del self.timer.activities[index]
        self.refresh_tree()

    def _outside_click(self, event):
        """Finish editing when clicking outside of entry widgets."""
        widget = event.widget
        entry_widgets = getattr(self, "entry_act", None), getattr(self, "time_act", None)
        if widget not in entry_widgets and widget is not self.tree:
            self.finish_edit(False)

    def on_tree_click(self, event):
        """Handle single click actions on the activity tree."""
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item:
            self.finish_edit(False)
            return
        if item == "add":
            self.finish_edit(False)
            self.add_activity()
            return
        if col == "#2":
            self.finish_edit(False)
            self.edit_activity(item)
        elif col == "#3":
            self.finish_edit(False)
            self.delete_activity(item)
        else:
            if getattr(self, "edit_item", None) and item != self.edit_item:
                self.finish_edit(False)

    def on_tree_double(self, event):
        """Double click opens the selected activity for editing."""
        item = self.tree.identify_row(event.y)
        if item and item != "add":
            self.finish_edit(False)
            self.edit_activity(item)

    def start_edit(self, iid):
        """Place entry widgets on top of the selected tree row."""
        self.finish_edit(False)
        self.edit_item = iid
        index = int(iid)
        act = self.timer.activities[index]
        name_box = self.tree.bbox(iid, column="#0")
        time_box = self.tree.bbox(iid, column="time")
        self.entry_act = ttk.Entry(self.tree)
        self.entry_act.insert(0, act.name)
        self.entry_act.place(x=name_box[0], y=name_box[1], width=name_box[2])
        self.time_act = TimeEntry(self.tree)
        self.time_act.set_seconds(act.duration)
        self.time_act.place(x=time_box[0], y=time_box[1], width=time_box[2])
        self.entry_act.focus_set()
        self.entry_act.bind("<Return>", lambda e: self.finish_edit(True))
        self.time_act.bind("<Return>", lambda e: self.finish_edit(True))

    def finish_edit(self, save):
        """Finalize editing of an activity, optionally saving changes."""
        if not hasattr(self, "edit_item") or self.edit_item is None:
            return
        name = self.entry_act.get().strip()
        duration = self.time_act.get_seconds()
        idx = int(self.edit_item)
        act = self.timer.activities[idx]
        changed = name != act.name or duration != act.duration
        if not save and changed:
            ans = messagebox.askyesnocancel(
                "Unsaved changes", "у вас есть несохраненные изменения"
            )
            if ans is None:
                return
            if ans:
                save = True
        if save:
            act.name = name
            act.duration = duration
        self.entry_act.destroy()
        self.time_act.destroy()
        self.edit_item = None
        self.refresh_tree()

    def save(self):
        """Validate inputs and write the timer to disk."""
        self.finish_edit(True)
        name = self.entry_name.get().strip()
        if not name or not re.fullmatch(r"[\w\- ]{1,50}", name):
            messagebox.showerror(
                "Invalid name",
                "Name must be 1-50 characters: letters, digits, spaces, '_' or '-'",
            )
            return
        desc = self.text_desc.get("1.0", "end").strip()
        if len(desc) > 200:
            messagebox.showerror(
                "Invalid description",
                "Description must be less than 200 characters",
            )
            return
        sets = int(self.spin_sets.get())
        if sets > 99:
            sets = 99
        self.timer.name = name
        self.timer.description = desc
        self.timer.sets = sets
        self.timer.rest_activity = self.time_rest_act.get_seconds()
        self.timer.rest_set = self.time_rest_set.get_seconds()
        self.manager.save_timer(self.timer)
        self.cancel()
