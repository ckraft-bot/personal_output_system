"""
main.py
-------
Prints a single receipt combining:
  - Today's date & time
  - A random motivational quote
  - Pending to-do tasks from tasks_bank.txt (skips lines marked with [x])

To mark a task complete: add [x] in front of it in tasks_bank.txt
  e.g.  [x] Make bed

Requires: pip install pywin32
Run with: python main.py
"""

import sys
import random
import textwrap
import win32print
from datetime import datetime

import quotes_bank
import print_quote
import print_todo

# ── Configuration ──────────────────────────────────────────────────────────────

PRINTER_NAME   = "Kraft POS-80C"
CHARS_PER_LINE = 30

# ── ESC/POS Helper Bytes ───────────────────────────────────────────────────────

ESC = b'\x1b'
GS  = b'\x1d'

CMD_INIT         = ESC + b'@'
CMD_ALIGN_CENTER = ESC + b'a' + b'\x01'
CMD_ALIGN_LEFT   = ESC + b'a' + b'\x00'
CMD_BOLD_ON      = ESC + b'E' + b'\x01'
CMD_BOLD_OFF     = ESC + b'E' + b'\x00'
CMD_FEED_4       = ESC + b'd' + b'\x04'
CMD_FEED_2       = ESC + b'd' + b'\x02'
CMD_FEED_1       = ESC + b'd' + b'\x01'
CMD_CUT_PARTIAL  = GS  + b'V' + b'\x01'

DIVIDER = b'- - - - - - - -\n'


# ── Receipt Builder ────────────────────────────────────────────────────────────

def build_receipt(quote: str, author: str, tasks: list[str]) -> bytes:
    """Assemble the full ESC/POS receipt combining quote, date/time and tasks."""
    data = b''
    now  = datetime.now()

    # ── Initialize
    data += CMD_INIT
    data += CMD_FEED_2

    # ── Date & Time (centered)
    data += CMD_ALIGN_CENTER
    data += DIVIDER
    date_str = now.strftime("%a  %B %d  %Y").encode("utf-8")
    time_str = now.strftime("%I:%M %p").encode("utf-8")
    data += date_str + b'\n'
    data += time_str + b'\n'
    data += DIVIDER
    data += CMD_FEED_1

    # ── Random Quote (left aligned, wrapped)
    data += CMD_ALIGN_LEFT
    for line in textwrap.wrap(quote, width=CHARS_PER_LINE):
        data += (line + '\n').encode('utf-8')

    # Attribution — bold, right-aligned
    data += CMD_FEED_1
    data += CMD_BOLD_ON
    attribution = f"-- {author}"
    data += (attribution.rjust(CHARS_PER_LINE) + '\n').encode('utf-8')
    data += CMD_BOLD_OFF

    # ── Tasks Section
    data += CMD_FEED_1
    data += CMD_ALIGN_CENTER
    data += DIVIDER
    data += CMD_BOLD_ON
    data += b"TODAY'S FOCUS\n"
    data += CMD_BOLD_OFF
    data += DIVIDER
    data += CMD_FEED_1

    # Task list
    data += CMD_ALIGN_LEFT
    if tasks:
        for task in tasks:
            lines = textwrap.wrap(task, width=CHARS_PER_LINE - 4)  # 4 chars for "[ ] "
            data += (f"[ ] {lines[0]}\n").encode('utf-8')
            for continuation in lines[1:]:
                data += (f"    {continuation}\n").encode('utf-8')
    else:
        data += CMD_ALIGN_CENTER
        data += CMD_BOLD_ON
        data += b"  All tasks complete!\n"
        data += CMD_BOLD_OFF

    # ── Footer
    data += CMD_FEED_1
    data += CMD_ALIGN_CENTER
    data += DIVIDER

    # ── Feed & Cut
    data += CMD_FEED_4
    data += CMD_CUT_PARTIAL

    return data


# ── Printer ────────────────────────────────────────────────────────────────────

def print_via_win32(printer_name: str, data: bytes):
    """Send raw bytes directly to a Windows printer."""
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Daily Focus Print", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, data)
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)
    print(f"✓ Sent to printer: {printer_name}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print_quote.check_printers_available()

    # Quote
    quote, author = print_quote.get_random_quote()

    # Tasks
    pending, completed = print_todo.get_all_tasks()
    print(f"Tasks: {len(pending)} pending, {len(completed)} completed.")

    # Build & preview in console
    now = datetime.now()
    print("\n--- Receipt preview (console) ---")
    print(now.strftime("%a  %B %d  %Y"))
    print(now.strftime("%I:%M %p"))
    print()
    for line in textwrap.wrap(quote, width=CHARS_PER_LINE):
        print(line)
    print(f"-- {author}".rjust(CHARS_PER_LINE))
    print()
    print("TODAY'S FOCUS")
    if pending:
        for task in pending:
            print(f"[ ] {task}")
    else:
        print("  All tasks complete!")
    print("---------------------------------\n")

    # Send to printer
    receipt_bytes = build_receipt(quote, author, pending)
    if sys.platform == "win32":
        print_via_win32(PRINTER_NAME, receipt_bytes)
    else:
        print("Non-Windows system detected.")
        print("For Linux, use: with open('/dev/usb/lp0', 'wb') as lp: lp.write(receipt_bytes)")


if __name__ == "__main__":
    main()