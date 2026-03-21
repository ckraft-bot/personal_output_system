"""
print_quote.py
--------------
Prints a randomly selected quote on the Kraft POS-80C printer
using raw ESC/POS commands over USB (Windows raw printer port).

Requirements:
    pip install pywin32

Usage:
    python print_quote.py

Notes:
    - The printer must be installed and visible in Windows as a printer.
    - Paper size: set custom size to 57mm x 99mm in printer properties.
"""

import sys
import random
import textwrap
import win32print
import quotes_bank as qb

# ── Configuration ──────────────────────────────────────────────────────────────

PRINTER_NAME = "Kraft POS-80C"

# 57mm paper at 203 dpi => ~48mm printable => ~30 chars per line at default font
CHARS_PER_LINE = 30


def get_random_quote() -> tuple[str, str]:
    """Pick a random author and one of their quotes.
    Skips any quotes containing non-ASCII characters (e.g. Chinese).
    Returns (quote, author)."""
    while True:
        author = random.choice(list(qb.QUOTES.keys()))
        quote  = random.choice(qb.QUOTES[author])
        if quote.isascii():
            return quote, author


# ── ESC/POS Helper Bytes ───────────────────────────────────────────────────────

ESC = b'\x1b'
GS  = b'\x1d'

CMD_INIT          = ESC + b'@'                  # Initialize printer
CMD_ALIGN_CENTER  = ESC + b'a' + b'\x01'        # Center alignment
CMD_ALIGN_LEFT    = ESC + b'a' + b'\x00'        # Left alignment
CMD_BOLD_ON       = ESC + b'E' + b'\x01'        # Bold on
CMD_BOLD_OFF      = ESC + b'E' + b'\x00'        # Bold off
CMD_DOUBLE_HEIGHT = ESC + b'!' + b'\x10'        # Double height text
CMD_NORMAL_SIZE   = ESC + b'!' + b'\x00'        # Normal text size
CMD_FEED_4        = ESC + b'd' + b'\x04'        # Feed 4 lines
CMD_FEED_2        = ESC + b'd' + b'\x02'        # Feed 2 lines
CMD_FEED_1        = ESC + b'd' + b'\x01'        # Feed 1 line
CMD_CUT_PARTIAL   = GS  + b'V' + b'\x01'        # Partial cut


# ── Helper Functions ───────────────────────────────────────────────────────────

def check_printers_available():
    """List all printers available on this Windows machine."""
    print("Available printers:")
    for p in win32print.EnumPrinters(2):
        print(f"  - {p[2]}")
    print()


def build_receipt(quote: str, author: str) -> bytes:
    """Assemble the full ESC/POS byte sequence for the quote receipt."""
    data = b''

    # Initialize
    data += CMD_INIT

    # Top padding
    data += CMD_FEED_2

    # Decorative header line (centered)
    data += CMD_ALIGN_CENTER
    data += b'- - - - - - - -\n'
    data += CMD_FEED_1

    # Quote body — wrap and print each line
    data += CMD_ALIGN_LEFT
    wrapped_lines = textwrap.wrap(quote, width=CHARS_PER_LINE)
    for line in wrapped_lines:
        data += (line + '\n').encode('utf-8')

    # Feed small gap before attribution
    data += CMD_FEED_1

    # Attribution — bold, right-aligned
    data += CMD_BOLD_ON
    attribution = f"-- {author}"
    padded_attr = attribution.rjust(CHARS_PER_LINE)
    data += (padded_attr + '\n').encode('utf-8')
    data += CMD_BOLD_OFF

    # Decorative footer line (centered)
    data += CMD_ALIGN_CENTER
    data += CMD_FEED_1
    data += b'- - - - - - - -\n'

    # Feed before cut
    data += CMD_FEED_4

    # Partial cut
    data += CMD_CUT_PARTIAL

    return data


# ── Printer Methods ────────────────────────────────────────────────────────────

def print_via_win32(printer_name: str, data: bytes):
    """Send raw bytes directly to a Windows printer."""
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Quote Print", None, "RAW"))
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
    check_printers_available()

    # Pick a random quote
    quote, author = get_random_quote()
    print(f"Selected quote by: {author}")

    receipt_bytes = build_receipt(quote, author)

    # Preview wrapped text in console
    print("\n--- Quote preview (console) ---")
    for line in textwrap.wrap(quote, width=CHARS_PER_LINE):
        print(line)
    print(f"-- {author}".rjust(CHARS_PER_LINE))
    print("-------------------------------\n")

    # Send to printer
    if sys.platform == "win32":
        print_via_win32(PRINTER_NAME, receipt_bytes)
    else:
        print("Non-Windows system detected.")
        print("For Linux, use: with open('/dev/usb/lp0', 'wb') as lp: lp.write(receipt_bytes)")


if __name__ == "__main__":
    main()