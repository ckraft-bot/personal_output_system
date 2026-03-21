# print_todo.py
# ── To-Do Task Manager ─────────────────────────────────────────────────────────
# Reads tasks from tasks_bank.txt.
# Lines starting with [x] are completed and skipped.
# Lines without [x] are pending and will be printed with [ ] checkboxes.
#
# Example tasks_bank.txt:
#   [x] Make bed
#   [x] Brush teeth
#   Put on clothes        ← still pending, will print
#   Eat breakfast         ← still pending, will print

import quotes_bank
import print_quote
import print_todo

TASKS_FILE = "tasks_bank.txt"


def get_pending_tasks() -> list[str]:
    """Return tasks that are not yet marked complete (no leading [x])."""
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"WARNING: '{TASKS_FILE}' not found. Create it with one task per line.")
        return []

    pending = []
    for line in lines:
        if line.lower().startswith("[x]"):
            continue  # already completed, skip
        # Strip any accidental [ ] prefix the user may have added manually
        task = line.lstrip("[ ]").strip() if line.startswith("[ ]") else line
        pending.append(task)

    return pending


def get_all_tasks() -> tuple[list[str], list[str]]:
    """Return (pending_tasks, completed_tasks) from tasks_bank.txt."""
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [], []

    pending   = []
    completed = []
    for line in lines:
        if line.lower().startswith("[x]"):
            completed.append(line[3:].strip())
        else:
            task = line.lstrip("[ ]").strip() if line.startswith("[ ]") else line
            pending.append(task)

    return pending, completed