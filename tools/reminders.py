from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
REMINDERS_PATH = BASE_DIR / "reminders.txt"


def add_reminder(time_str: str, text: str) -> str:
    time_str = time_str.strip()
    text = text.strip()
    if not time_str or not text:
        return "Формат: напомни в ЧЧ:ММ: текст"
    line = time_str + "|" + text + "\n"
    with REMINDERS_PATH.open("a", encoding="utf-8") as f:
        f.write(line)
    return "Напоминание добавлено: в " + time_str + " — " + text


def list_reminders() -> str:
    if not REMINDERS_PATH.exists():
        return "Напоминаний нет."
    lines = REMINDERS_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        return "Напоминаний нет."
    result = []
    for i, line in enumerate(lines, 1):
        parts = line.split("|", 1)
        if len(parts) == 2:
            result.append(str(i) + ". В " + parts[0] + " — " + parts[1])
    return "Напоминания:\n\n" + "\n".join(result)


def get_due_reminders() -> list:
    if not REMINDERS_PATH.exists():
        return []
    now = datetime.now().strftime("%H:%M")
    lines = REMINDERS_PATH.read_text(encoding="utf-8").splitlines()
    due = []
    remaining = []
    for line in lines:
        parts = line.split("|", 1)
        if len(parts) == 2 and parts[0].strip() == now:
            due.append(parts[1].strip())
        else:
            remaining.append(line)
    REMINDERS_PATH.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return due
