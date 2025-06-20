import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import re

PAID = "ОПЛАЧЕНО"
INVOICED = "СЧЕТ ВЫСТАВЛЕН"
DATE_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")
TIME_PATTERN = re.compile(r"\d{1,2}:\d{2}")


def compute_interval(lines):
    total_minutes = 0.0
    start_date = None
    end_date = None
    current_date = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if DATE_PATTERN.match(line):
            current_date = line
            if start_date is None:
                start_date = current_date
            end_date = current_date
            i += 1
            continue
        if TIME_PATTERN.match(line):
            block_times = []
            while i < len(lines) and lines[i] and not DATE_PATTERN.match(lines[i]):
                block_times.extend(TIME_PATTERN.findall(lines[i]))
                i += 1
            if len(block_times) >= 2:
                t1 = datetime.strptime(block_times[0], "%H:%M")
                t2 = datetime.strptime(block_times[-1], "%H:%M")
                delta = (t2 - t1).total_seconds() / 60
                if delta < 0:
                    delta += 24 * 60
                total_minutes += delta
            continue
        i += 1
    return total_minutes, start_date, end_date


def parse_intervals(lines):
    intervals = []
    current_date = None
    times = []
    start_idx = 0
    for idx, line in enumerate(lines):
        if DATE_PATTERN.match(line):
            if times:
                intervals.append({
                    "date": current_date,
                    "start": times[0],
                    "end": times[-1],
                    "start_idx": start_idx,
                    "end_idx": idx - 1,
                })
                times = []
            current_date = line
            start_idx = idx
        elif TIME_PATTERN.search(line):
            times.extend(TIME_PATTERN.findall(line))
        elif PAID in line or INVOICED in line:
            if times:
                intervals.append({
                    "date": current_date,
                    "start": times[0],
                    "end": times[-1],
                    "start_idx": start_idx,
                    "end_idx": idx - 1,
                })
                times = []
            intervals.append({"status": line.strip(), "idx": idx})
    if times:
        intervals.append({
            "date": current_date,
            "start": times[0],
            "end": times[-1],
            "start_idx": start_idx,
            "end_idx": len(lines) - 1,
        })
    return intervals


def intervals_with_statuses(lines):
    intervals = parse_intervals(lines)
    paid_indexes = [i for i, line in enumerate(lines) if PAID in line]
    last_paid = paid_indexes[-1] if paid_indexes else -1
    invoice_index = None
    for idx in range(last_paid + 1, len(lines)):
        if INVOICED in lines[idx]:
            invoice_index = idx
            break
    result = []
    for item in intervals:
        if "status" in item:
            continue
        if item["end_idx"] <= last_paid:
            st = "PAID"
        elif invoice_index is not None and item["start_idx"] < invoice_index:
            st = "INVOICED"
        else:
            st = "UNPAID"
        result.append(f"{item['date']} {item['start']} - {item['end']} {st}")
    return result


def compute_totals(lines):
    paid_indexes = [i for i, line in enumerate(lines) if PAID in line]
    last_paid_index = paid_indexes[-1] if paid_indexes else -1
    post_paid = lines[last_paid_index + 1 :]
    total_minutes, start_date, end_date = compute_interval(post_paid)
    next_invoice_index = None
    for idx in range(last_paid_index + 1, len(lines)):
        if INVOICED in lines[idx]:
            next_invoice_index = idx
            break
    invoiced_minutes = None
    invoiced_end_date = None
    if next_invoice_index is not None:
        invoiced_lines = lines[last_paid_index + 1 : next_invoice_index]
        invoiced_minutes, _, invoiced_end_date = compute_interval(invoiced_lines)
    unissued_start = next_invoice_index if next_invoice_index is not None else last_paid_index
    unissued_lines = lines[unissued_start + 1 :]
    unissued_minutes, unissued_start_date, unissued_end_date = compute_interval(unissued_lines)
    res = []
    if total_minutes:
        res.append(f"{round(total_minutes / 30) / 2} часов (с {start_date} по {end_date})")
    if invoiced_minutes is not None:
        res.append(
            f"{round(invoiced_minutes / 30) / 2} часов до {INVOICED} (с {start_date} по {invoiced_end_date})"
        )
    if unissued_minutes:
        res.append(
            f"{round(unissued_minutes / 30) / 2} часов без {INVOICED} (с {unissued_start_date} по {unissued_end_date})"
        )
    return "\n".join(res)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Timecounter GUI")
        self.geometry("600x500")
        self.logfile = None

        file_btn = tk.Button(self, text="Select Log File", command=self.select_file)
        file_btn.pack(pady=5)

        self.interval_list = tk.Listbox(self, width=80)
        self.interval_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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

    def select_file(self):
        path = filedialog.askopenfilename(title="Select log file", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.logfile = path
            self.refresh_list()

    def read_lines(self):
        if not self.logfile or not os.path.exists(self.logfile):
            return []
        with open(self.logfile, encoding="utf-8") as fh:
            return [l.strip() for l in fh.readlines()]

    def refresh_list(self):
        lines = self.read_lines()
        display = intervals_with_statuses(lines)
        self.interval_list.delete(0, tk.END)
        for d in display:
            self.interval_list.insert(tk.END, d)

    def add_note(self):
        if not self.logfile:
            messagebox.showwarning("No file", "Select a log file first")
            return
        date = self.date_var.get().strip()
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        note = self.note_var.get().strip()
        if not (DATE_PATTERN.match(date) and TIME_PATTERN.match(start) and TIME_PATTERN.match(end)):
            messagebox.showerror("Invalid", "Enter valid date and times")
            return
        lines = self.read_lines()
        with open(self.logfile, "a", encoding="utf-8") as fh:
            if not lines or lines[-1] != date:
                fh.write(date + "\n\n")
            fh.write(f"{start} {note}\n")
            fh.write(f"{end}\n")
        self.refresh_list()

    def show_totals(self):
        lines = self.read_lines()
        if not lines:
            messagebox.showinfo("Totals", "No data")
            return
        msg = compute_totals(lines)
        messagebox.showinfo("Totals", msg)

    def mark_paid(self):
        if not self.logfile:
            return
        lines = self.read_lines()
        paid_indexes = [i for i, line in enumerate(lines) if PAID in line]
        last_paid_index = paid_indexes[-1] if paid_indexes else -1
        next_invoice_index = None
        for idx in range(last_paid_index + 1, len(lines)):
            if INVOICED in lines[idx]:
                next_invoice_index = idx
                break
        if next_invoice_index is not None:
            lines[next_invoice_index] = lines[next_invoice_index].replace(INVOICED, PAID)
            with open(self.logfile, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            messagebox.showinfo("Marked", "Invoice marked as paid")
            self.refresh_list()
        else:
            messagebox.showinfo("Info", "No invoice found")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
