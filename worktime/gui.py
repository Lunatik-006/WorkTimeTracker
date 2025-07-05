import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from datetime import datetime
from typing import Optional, List

from .counter import TimeCounter
from .constants import (
    DATE_PATTERN,
    TIME_PATTERN,
    DEFAULT_LOG_DIR,
    INVOICED,
    PAID,
    UNPAID,
)


def _format_partial_date(digits: str) -> str:
    """Return a partially formatted date from up to 8 digit characters."""
    digits = digits[:8]
    if len(digits) <= 4:
        return digits
    if len(digits) <= 6:
        return f"{digits[:4]}.{digits[4:]}"
    return f"{digits[:4]}.{digits[4:6]}.{digits[6:]}"


class StatusDialog(simpledialog.Dialog):
    """Popup offering predefined status choices."""

    def body(self, master: tk.Frame) -> None:
        self.result = None
        for st in (PAID, INVOICED, UNPAID):
            tk.Button(
                master,
                text=st,
                width=15,
                command=lambda s=st: self._set(s),
            ).pack(padx=5, pady=2, fill=tk.X)

    def buttonbox(self) -> None:  # remove default buttons
        pass

    def _set(self, value: str) -> None:
        self.result = value
        self.destroy()


class DateEntryDialog(simpledialog.Dialog):
    """Dialog with a smart date entry field."""

    def __init__(self, master: tk.Misc, title: str, initial: str,
                 existing: List[str]):
        self.initial = initial
        self.existing = existing
        super().__init__(master, title)

    def body(self, master: tk.Frame) -> tk.Widget:
        self.var = tk.StringVar(value=self.initial)
        entry = tk.Entry(master, textvariable=self.var)
        entry.pack(padx=5, pady=5)
        entry.bind("<FocusIn>", self._clear_default)
        entry.bind("<KeyRelease>", self._format_date)
        return entry

    def _clear_default(self, _event: tk.Event) -> None:
        if self.var.get() == self.initial:
            self.var.set("")

    def _format_date(self, _event: tk.Event) -> None:
        digits = "".join(ch for ch in self.var.get() if ch.isdigit())
        self.var.set(_format_partial_date(digits))

    def validate(self) -> bool:
        value = self.var.get()
        if value in self.existing:
            messagebox.showerror("Error", "Date already exists")
            return False
        if not DATE_PATTERN.match(value):
            messagebox.showerror("Error", "Format YYYY.MM.DD")
            return False
        try:
            datetime.strptime(value, "%Y.%m.%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date")
            return False
        return True

    def apply(self) -> None:
        self.result = self.var.get()


class PeriodDialog(simpledialog.Dialog):
    """Dialog to specify start and end dates for a new period."""

    def __init__(self, master: tk.Misc, existing: List[str]):
        self.existing = existing
        super().__init__(master, "New Period")

    def body(self, master: tk.Frame) -> tk.Widget:
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        tk.Label(master, text="Start date:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.start_entry = tk.Entry(master, textvariable=self.start_var)
        self.start_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(master, text="End date:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.end_entry = tk.Entry(master, textvariable=self.end_var)
        self.end_entry.grid(row=1, column=1, padx=5, pady=2)
        for e in (self.start_entry, self.end_entry):
            e.bind("<KeyRelease>", self._format)
        return self.start_entry

    def _format(self, event: tk.Event) -> None:
        var = event.widget
        if var not in (self.start_entry, self.end_entry):
            return
        digits = "".join(ch for ch in var.get() if ch.isdigit())
        var.delete(0, tk.END)
        var.insert(0, _format_partial_date(digits))

    def validate(self) -> bool:
        start = self.start_var.get()
        end = self.end_var.get()
        for val in (start, end):
            if not DATE_PATTERN.match(val):
                messagebox.showerror("Error", "Format YYYY.MM.DD")
                return False
            try:
                datetime.strptime(val, "%Y.%m.%d")
            except ValueError:
                messagebox.showerror("Error", f"Invalid date {val}")
                return False
        if start not in self.existing or end not in self.existing:
            messagebox.showerror("Error", "Date not found in log")
            return False
        if self.existing.index(start) > self.existing.index(end):
            messagebox.showerror("Error", "Start date after end date")
            return False
        return True

    def apply(self) -> None:
        self.result = (self.start_var.get(), self.end_var.get())


class DateEditDialog(simpledialog.Dialog):
    """Dialog to edit a date line and all its notes."""

    def __init__(self, master: tk.Misc, tc: TimeCounter, index: int):
        self.tc = tc
        self.index = index
        end = index
        for i in range(index + 1, len(tc.lines)):
            line = tc.lines[i]
            if DATE_PATTERN.match(line) or PAID in line or INVOICED in line:
                break
            end = i
        self.lines = tc.lines[index + 1 : end + 1]
        self.initial_date = tc.lines[index]
        self.existing = [
            l
            for j, l in enumerate(tc.lines)
            if DATE_PATTERN.match(l) and j != index
        ]
        super().__init__(master, "Edit date")

    def body(self, master: tk.Frame) -> tk.Widget:
        self.date_var = tk.StringVar(value=self.initial_date)
        self.date_entry = tk.Entry(master, textvariable=self.date_var)
        self.date_entry.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.date_entry.bind("<KeyRelease>", self._format_date)
        self.rows: List[tuple] = []
        for i, line in enumerate(self.lines):
            t_var = tk.StringVar()
            n_var = tk.StringVar()
            m = TIME_PATTERN.match(line or "")
            t_val = m.group() if m else ""
            note = line[m.end():].lstrip() if m else line
            t_var.set(t_val)
            n_var.set(note)
            te = tk.Entry(master, textvariable=t_var, width=5)
            ne = tk.Entry(master, textvariable=n_var)
            te.grid(row=i + 1, column=0, padx=2, pady=2, sticky="w")
            ne.grid(row=i + 1, column=1, padx=2, pady=2, sticky="ew")
            self.rows.append((t_var, n_var, te, ne))
        master.columnconfigure(1, weight=1)
        self._setup_navigation()
        return self.date_entry

    def _setup_navigation(self) -> None:
        count = len(self.rows)
        for i, (_, _, te, ne) in enumerate(self.rows):
            te.bind("<KeyRelease>", lambda e, v=self.rows[i][0]: self._auto_colon(v))
            if i > 0:
                te.bind("<Up>", lambda e, r=i - 1: self.rows[r][2].focus_set())
                ne.bind("<Up>", lambda e, r=i - 1: self.rows[r][3].focus_set())
            if i < count - 1:
                te.bind("<Down>", lambda e, r=i + 1: self.rows[r][2].focus_set())
                ne.bind("<Down>", lambda e, r=i + 1: self.rows[r][3].focus_set())
            te.bind("<Right>", lambda e, r=i: self.rows[r][3].focus_set())
            ne.bind("<Left>", lambda e, r=i: self.rows[r][2].focus_set())
            for w in (te, ne):
                w.bind("<Return>", lambda e: self.ok())

    def _auto_colon(self, var: tk.StringVar) -> None:
        val = var.get()
        if len(val) == 2 and ":" not in val:
            var.set(val + ":")

    def _format_date(self, _event: tk.Event) -> None:
        digits = "".join(ch for ch in self.date_var.get() if ch.isdigit())
        self.date_var.set(_format_partial_date(digits))

    def validate(self) -> bool:
        date = self.date_var.get()
        if date in self.existing:
            messagebox.showerror("Error", "Date already exists")
            return False
        if not DATE_PATTERN.match(date):
            messagebox.showerror("Error", "Format YYYY.MM.DD")
            return False
        try:
            datetime.strptime(date, "%Y.%m.%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date")
            return False
        for t_var, _, _, _ in self.rows:
            t_val = t_var.get()
            if t_val and not TIME_PATTERN.match(t_val):
                messagebox.showerror("Error", f"Invalid time: {t_val}")
                return False
        return True

    def apply(self) -> None:
        self.result = {
            "date": self.date_var.get(),
            "lines": [
                f"{t.get()} {n.get()}".rstrip() for t, n, _, _ in self.rows
            ],
        }



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

    def _capture_state(self) -> dict:
        state = {"open": set(), "focus": None}
        def recurse(node: str):
            if self.tree.item(node, "open"):
                tag = self.tree.item(node, "tags")[0]
                idx = self.tree.set(node, "idx")
                state["open"].add((tag, idx))
            for ch in self.tree.get_children(node):
                recurse(ch)
        for top in self.tree.get_children(""):
            recurse(top)
        focus = self.tree.focus()
        if focus:
            tag = self.tree.item(focus, "tags")[0]
            idx = self.tree.set(focus, "idx")
            state["focus"] = (tag, idx)
        return state

    def _restore_state(self, state: dict) -> None:
        if not state:
            return
        def recurse(node: str):
            tag = self.tree.item(node, "tags")[0]
            idx = self.tree.set(node, "idx")
            if (tag, idx) in state.get("open", set()):
                self.tree.item(node, open=True)
            for ch in self.tree.get_children(node):
                recurse(ch)
        for top in self.tree.get_children(""):
            recurse(top)
        focus = state.get("focus")
        if focus:
            for item in self.tree.get_children(""):
                found = self._find_by_key(item, focus)
                if found:
                    self.tree.focus(found)
                    break

    def _find_by_key(self, node: str, key: tuple) -> Optional[str]:
        tag = self.tree.item(node, "tags")[0]
        idx = self.tree.set(node, "idx")
        if (tag, idx) == key:
            return node
        for ch in self.tree.get_children(node):
            res = self._find_by_key(ch, key)
            if res:
                return res
        return None

    def refresh_list(self, preserve: bool = False) -> None:
        state = self._capture_state() if preserve else None
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
        if preserve:
            self._restore_state(state)

    # ----------------------------------------------------- context menu
    def on_tree_click(self, event: tk.Event) -> None:
        if self.edit_frame is not None:
            x_root = self.tree.winfo_rootx() + event.x
            y_root = self.tree.winfo_rooty() + event.y
            if not self.edit_frame.winfo_containing(x_root, y_root):
                self.finish_edit()
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
            self.context_menu.add_command(label="Удалить", command=lambda i=item: self.delete_period(i))
        elif "date" in tags:
            self.context_menu.add_command(label="Ред.", command=lambda i=item: self.edit_date(i))
            self.context_menu.add_command(label="+Дата", command=lambda i=item: self.add_date(i))
            self.context_menu.add_command(label="+Заметка", command=lambda i=item: self.add_note_to_date(i))
            self.context_menu.add_command(label="Удалить", command=lambda i=item: self.delete_date(i))
        elif "note" in tags:
            self.context_menu.add_command(label="Ред.", command=lambda i=item: self.start_edit_note(i))
            self.context_menu.add_command(label="+", command=lambda i=item: self.add_note_after(i))
            self.context_menu.add_command(label="Удалить", command=lambda i=item: self.delete_note(i))
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
        self.refresh_list(preserve=True)

    # ----------------------------------------------------- actions used by popup buttons
    def add_note_after(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        now = datetime.now().strftime("%H:%M")
        self.tc.insert_line_after(index, now)
        self.refresh_list(preserve=True)
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
        existing = [l for l in self.tc.lines if DATE_PATTERN.match(l)]
        dlg = DateEntryDialog(
            self,
            "Date",
            datetime.now().strftime("%Y.%m.%d"),
            existing,
        )
        if dlg.result:
            self.tc.insert_date_after(index, dlg.result)
            self.refresh_list(preserve=True)

    def edit_date(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        dlg = DateEditDialog(self, self.tc, index)
        if dlg.result:
            self.tc.update_line(index, dlg.result["date"])
            for off, line in enumerate(dlg.result["lines"]):
                self.tc.update_line(index + 1 + off, line)
            self.refresh_list(preserve=True)

    def change_status(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        dlg = StatusDialog(self, "Status")
        if dlg.result:
            self.tc.change_status(index, dlg.result)
            self.refresh_list(preserve=True)

    def add_period(self) -> None:
        if not self.tc:
            return
        existing = [l for l in self.tc.lines if DATE_PATTERN.match(l)]
        dlg = PeriodDialog(self, existing)
        if dlg.result:
            start, end = dlg.result
            self.tc.add_custom_period(start, end)
            self.refresh_list(preserve=True)

    def add_note_to_date(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        now = datetime.now().strftime("%H:%M")
        self.tc.insert_line_after(index, now)
        self.refresh_list(preserve=True)
        self.edit_note_by_index(index + 1)

    def delete_note(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        if messagebox.askokcancel("Delete", "Delete note?"):
            self.tc.delete_lines(index, index)
            self.refresh_list(preserve=True)

    def delete_date(self, item: str) -> None:
        index = int(self.tree.set(item, "idx"))
        info = None
        for p in self.tc.parse_periods():
            for d in p.get("dates", []):
                if d["start_idx"] == index:
                    info = d
                    break
            if info:
                break
        if info and messagebox.askokcancel("Delete", "Delete date?"):
            self.tc.delete_lines(info["start_idx"], info["end_idx"])
            self.refresh_list(preserve=True)

    def delete_period(self, item: str) -> None:
        status_idx = int(self.tree.set(item, "idx"))
        periods = self.tc.parse_periods()
        target = None
        for p in periods:
            if self._status_index(p) == status_idx or (status_idx == -1 and p["start_idx"] == int(self.tree.set(item, "idx"))):
                target = p
                break
        if target and messagebox.askokcancel("Delete", "Delete period?"):
            end = self._status_index(target)
            if end == -1:
                end = target["end_idx"]
            self.tc.delete_lines(target.get("start_idx", 0), end)
            self.refresh_list(preserve=True)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
