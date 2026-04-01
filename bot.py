import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")

TASKS_FILE = "tasks_bank.txt"

def read_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return f.readlines()

def write_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        f.writelines(tasks)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "你好! I'm Xi Guan 习惯, your daily habit assistant.\n\n"
        "Commands:\n"
        "/add <task> — add a task\n"
        "/complete <task> — mark a task done\n"
        "/list — see pending tasks\n"
        "/print — print your receipt"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Usage: /add <task>")
        return
    tasks = read_tasks()
    tasks.append(task + "\n")
    write_tasks(tasks)
    await update.message.reply_text(f"Added: {task}")

async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Usage: /complete <task>")
        return
    tasks = read_tasks()
    updated = []
    found = False
    for t in tasks:
        if t.strip().lower() == task.lower():
            updated.append(f"[x] {t.strip()}\n")
            found = True
        else:
            updated.append(t)
    write_tasks(updated)
    msg = f"✓ Marked complete: {task}" if found else f"Task not found: {task}"
    await update.message.reply_text(msg)

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = read_tasks()
    pending = [t.strip() for t in tasks if not t.startswith("[x]")]
    if not pending:
        await update.message.reply_text("No pending tasks! 🎉")
    else:
        await update.message.reply_text("\n".join(f"• {t}" for t in pending))

async def print_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    os.system("python main.py")
    await update.message.reply_text("Receipt printed! 🧾")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("complete", complete))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("print", print_receipt))

print("Xi Guan 习惯 is running...")
app.run_polling()
