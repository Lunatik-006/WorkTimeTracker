import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from timecounter import TimeCounter, DATE_PATTERN, TIME_PATTERN


class App(tk.Tk):
    """Simple graphical interface for :class:`TimeCounter`."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Timecounter GUI")
        self.geometry("600x500")
        self.tc: Optional[TimeCounter] = None

        file_btn = tk.Button(self, text="Select Log File", command=self.select_file)
        file_btn.pack(pady=5)

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        form = tk.Frame(self)
        form.pack(pady=5)
        tk.Label(form, text="Date (YYYY.MM.DD)").grid(row=0, column=0)
        tk.Label(form, text="Start HH:MM").grid(row=1, column=0)
        tk.Label(form, text="End HH:MM").grid(row=2, column=0)
        tk.Label(form, text="Note").grid(row=3, column=0)

        self.date_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.note_var = tk.StringVar()

        tk.Entry(form, textvariable=self.date_var).grid(row=0, column=1)
        tk.Entry(form, textvariable=self.start_var).grid(row=1, column=1)
        tk.Entry(form, textvariable=self.end_var).grid(row=2, column=1)
        tk.Entry(form, textvariable=self.note_var).grid(row=3, column=1)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Note", command=self.add_note).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Calculate Totals", command=self.show_totals).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Mark Invoice as Paid", command=self.mark_paid).grid(row=0, column=2, padx=5)

    def select_file(self) -> None:
        path = filedialog.askopenfilename(title="Select log file", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.tc = TimeCounter(path)
            self.refresh_list()

    def refresh_list(self) -> None:
        for child in self.tree.get_children():
            self.tree.delete(child)
        if not self.tc:
            return
        for period in self.tc.parse_periods():
            period_text = f"{period.get('start','')} - {period.get('end','')} {period.get('status','')}".strip()
            pid = self.tree.insert("", tk.END, text=period_text)
            for date in period.get("dates", []):
                did = self.tree.insert(pid, tk.END, text=date["date"])
                for note in date.get("notes", []):
                    self.tree.insert(did, tk.END, text=note)

    def add_note(self) -> None:
        if not self.tc:
            messagebox.showwarning("No file", "Select a log file first")
            return
        date = self.date_var.get().strip()
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        note = self.note_var.get().strip()
        if not (DATE_PATTERN.match(date) and TIME_PATTERN.match(start) and TIME_PATTERN.match(end)):
            messagebox.showerror("Invalid", "Enter valid date and times")
            return
        self.tc.add_entry(date, start, end, note)
        self.refresh_list()

    def show_totals(self) -> None:
        if not self.tc:
            messagebox.showinfo("Totals", "No data")
            return
        messagebox.showinfo("Totals", self.tc.compute_totals())

    def mark_paid(self) -> None:
        if not self.tc:
            return
        if self.tc.mark_invoice_as_paid():
            messagebox.showinfo("Marked", "Invoice marked as paid")
        else:
            messagebox.showinfo("Info", "No invoice found")
        self.refresh_list()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

