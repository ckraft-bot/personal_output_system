# POS: Personal Output System
An executive function assistant that prints a daily focus receipt on a thermal printer. Each receipt combines the current datetime, a randomly selected quote, and your pending to-do tasks for the day.

---

## First Run
- _the output_

![First Run](Media/first_run.jpeg)

- _the demo (printing)_

![First Run](Media/first_run.gif)

- _the demo (integating with telegram)_ [watch the walkthorugh here](https://youtu.be/HqYRTd6m334?si=__qfN-KE2ELJ53mr)

---

## How to Use

**1. Start Xi Guan 习惯** — run the Telegram bot in a terminal:
```bash
python bot.py
```

**2. Add your tasks** — message your bot on Telegram:
```
/add Make bed
/add Brush teeth
/add Eat breakfast
/add Drink coffee
/add Reply to emails
```

**3. Mark tasks complete** — when you finish a task, tell the bot:
```
/complete Make bed
/complete Brush teeth
```

**4. Check what's left** — see your pending tasks anytime:
```
/list
```

**5. Print your receipt** — trigger the printer from Telegram:
```
/print
```

Only pending tasks will appear on the receipt.

---

## Bot Setup

Xi Guan 习惯 is a Telegram bot that manages your `tasks_bank.txt` without you ever needing to open the file.

**1. Create your bot via BotFather on Telegram and copy your token.**

**2. Create a `.env` file in the project root:**
```
TELEGRAM_BOT_TOKEN=your_token_here
```

**3. Install dependencies:**
```bash
pip install python-telegram-bot python-dotenv
```

**4. Run the bot:**
```bash
python bot.py
```

---

## Managing Quotes

Quotes are stored in `quotes_bank.py` as a dictionary organised by author.
```python
"Author Name": [
    "First quote here.",
    "Second quote here.",
],
```

Each time the program runs, one author and one of their quotes is selected at random.
