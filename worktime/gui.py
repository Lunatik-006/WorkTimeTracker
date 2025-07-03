import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from datetime import datetime
from typing import Optional

from .counter import TimeCounter
from .constants import DATE_PATTERN, TIME_PATTERN, DEFAULT_LOG_DIR, INVOICED, PAID


class App(tk.Tk):
    """Graphical interface for :class:`TimeCounter` with inline editing."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Timecounter GUI")
        self.geometry("600x500")
        self.tc: Optional[TimeCounter] = None

        file_frame = tk.Frame(self)
        file_frame.pack(pady=5)
        tk.Button(file_frame, text="Select Log File", command=self.select_file).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Create New Log", command=self.create_new_log).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(self, columns=("idx", "menu"))
        self.tree.column("idx", width=0, stretch=False)
        self.tree.column("menu", width=20, anchor="e", stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_tree_click)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.edit_frame: Optional[tk.Frame] = None
        self.edit_item: Optional[str] = None
        self.edit_index: Optional[int] = None
        self.edit_time_var: Optional[tk.StringVar] = None
        self.edit_text_var: Optional[tk.StringVar] = None

    # ----------------------------------------------------- file operations
    def select_file(self) -> None:
        path = filedialog.askopenfilename(title="Select log file", filetypes=[("Text", "*.txt"), ("All", "*.*")], initialdir=DEFAULT_LOG_DIR)
        if path:
            self.tc = TimeCounter(path)
            self.refresh_list()

    def create_new_log(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")], initialdir=DEFAULT_LOG_DIR)
        if path:
            open(path, "a").close()
            self.tc = TimeCounter(path)
            self.refresh_list()

    # ----------------------------------------------------- tree population
    def _status_index(self, period: dict) -> int:
        idx = period.get("end_idx", -1) + 1
        if idx < len(self.tc.lines) and (INVOICED in self.tc.lines[idx] or PAID in self.tc.lines[idx]):
            return idx
        return -1

    def refresh_list(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if not self.tc:
            return
        periods = self.tc.parse_periods()
        for p in periods:
            pidx = self._status_index(p)
            text = f"{p.get('start','')} - {p.get('end','')} {p.get('total_hours',0)} ч. {p.get('status','')}".strip()
            pid = self.tree.insert("", tk.END, text=text, tags=("period",), values=(pidx, "⋮"))
            for d in p.get("dates", []):
                hours = d.get("hours", 0)
                hours_str = ("%.1f" % hours).rstrip("0").rstrip(".")
                did = self.tree.insert(pid, tk.END, text=f"{d['date']} {hours_str} ч.", tags=("date",), values=(d["start_idx"], "⋮"))
                for line_idx in range(d["start_idx"] + 1, d["end_idx"] + 1):
                    line = self.tc.lines[line_idx]
                    display = line if line else "------------"
                    self.tree.insert(did, tk.END, text=display, tags=("note",), values=(line_idx, "⋮"))

    # ----------------------------------------------------- context menu
    def on_tree_click(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if col == "#2" and item:
            self.show_menu(item, event.x_root, event.y_root)
            return "break"

    def show_menu(self, item: str, x: int, y: int) -> None:
        self.context_menu.delete(0, tk.END)
        tags = self.tree.item(item, "tags")
        if "period" in tags:
            self.context_menu.add_command(label="Статус", command=lambda i=item: self.change_status(i))
            self.context_menu.add_command(label="+Период", command=self.add_period)
        elif "date" in tags:
            self.context_menu.add_command(label="Ред.", command=lambda i=item: self.edit_date(i))
            self.context_menu.add_command(label="+Дата", command=lambda i=item: self.add_date(i))
        elif "note" in tags:
            self.context_menu.add_command(label="Ред.", command=lambda i=item: self.start_edit_note(i))
            self.context_menu.add_command(label="+", command=lambda i=item: self.add_note_after(i))
        else:
            return
        self.context_menu.tk_popup(x, y)

    # ----------------------------------------------------- editing helpers
    def _validate_time(self, value: str) -> bool:
        if not TIME_PATTERN.match(value):
            return False
        try:
            hh, mm = map(int, value.split(":"))
        except ValueError:
            return False
        return 0 <= hh <= 23 and 0 <= mm <= 55

    def _auto_colon(self, *_: tk.Event) -> None:
        if self.edit_time_var is None:
            return
        val = self.edit_time_var.get()
        if len(val) == 2 and ":" not in val:
            self.edit_time_var.set(val + ":")

    def on_double_click(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        if item and "note" in self.tree.item(item, "tags"):
            self.start_edit_note(item)

    def start_edit_note(self, item: str) -> None:
        if self.edit_frame is not None:
            self.edit_frame.destroy()
        index = int(self.tree.set(item, "idx"))
        text = self.tree.item(item, "text")
        match = TIME_PATTERN.match(text or "")
        time_part = match.group() if match else ""
        note_part = text[match.end():].lstrip() if match else text
        bbox = self.tree.bbox(item)
        if not bbox:
            return
        x, y, width, height = bbox
        self.edit_time_var = tk.StringVar(value=time_part)
        self.edit_text_var = tk.StringVar(value=note_part)
        self.edit_frame = tk.Frame(self.tree)
        time_entry = tk.Entry(self.edit_frame, textvariable=self.edit_time_var, width=5)
        text_entry = tk.Entry(self.edit_frame, textvariable=self.edit_text_var)
        time_entry.pack(side=tk.LEFT)
        text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        time_entry.focus_set()
        time_entry.bind("<KeyRelease>", self._auto_colon)
        for w in (time_entry, text_entry):
            w.bind("<Return>", lambda e: self.finish_edit())
        self.edit_frame.place(x=x, y=y, width=width)
        self.edit_item = item
        self.edit_index = index

    def finish_edit(self) -> None:
        if self.edit_frame is None or self.edit_index is None:
            return
        time_val = self.edit_time_var.get()
        text_val = self.edit_text_var.get().strip()
        if not self._validate_time(time_val):
            messagebox.showerror("Invalid time", "Enter time between 00:00 and 23:55")
            return
        line = f"{time_val} {text_val}".rstrip()
        self.tc.update_line(self.edit_index, line)
        self.edit_frame.destroy()
        self.edit_frame = None
        self.refresh_list()

    # ----------------------------------------------------- actions used by popup buttons
    def add_note_after(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        now = datetime.now().strftime("%H:%M")
        self.tc.insert_line_after(index, now)
        self.refresh_list()
        self.edit_note_by_index(index + 1)

    def edit_note_by_index(self, index: int) -> None:
        def search(node: str) -> Optional[str]:
            if int(self.tree.set(node, "idx") or -1) == index:
                return node
            for ch in self.tree.get_children(node):
                res = search(ch)
                if res:
                    return res
            return None
        for top in self.tree.get_children(""):
            found = search(top)
            if found:
                self.start_edit_note(found)
                return

    def add_date(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        date = simpledialog.askstring("Date", "YYYY.MM.DD")
        if date and DATE_PATTERN.match(date):
            self.tc.insert_date_after(index, date)
            self.refresh_list()

    def edit_date(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        current = self.tree.item(item, "text").split()[0]
        new = simpledialog.askstring("Edit date", "YYYY.MM.DD", initialvalue=current)
        if new and DATE_PATTERN.match(new):
            self.tc.update_line(index, new)
            self.refresh_list()

    def change_status(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        status = simpledialog.askstring("Status", f"{PAID}/{INVOICED}")
        if status:
            self.tc.change_status(index, status)
            self.refresh_list()

    def add_period(self) -> None:
        if self.tc.mark_last_period_as_invoiced():
            self.refresh_list()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
