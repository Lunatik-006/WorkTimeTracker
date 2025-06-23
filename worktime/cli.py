from __future__ import annotations
import argparse
from typing import List, Optional

from .counter import TimeCounter


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Count working time blocks")
    parser.add_argument("logfile", help="Path to the log file")
    args = parser.parse_args(argv)

    tc = TimeCounter(args.logfile)

    print(tc.compute_totals())

    if tc.mark_invoice_as_paid():
        print("Marked invoice as paid.")

    add = input("Add more log lines? [y/N] ").strip().lower()
    if add.startswith("y"):
        print("Enter log lines. Submit an empty line to finish:")
        while True:
            entry = input()
            if entry == "":
                break
            tc.lines.append(entry)
        tc.save()


if __name__ == "__main__":
    main()
