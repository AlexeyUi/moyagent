import time
import os
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tools.reminders import get_due_reminders
from tools.calendar_store import get_dates_for_today, get_dates_for_date

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str):
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    try:
        httpx.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)


def check_day_type():
    """Проверяет тип дня через isdayoff.ru и отправляет утреннее сообщение в 8:00"""
    now = datetime.now()
    if now.hour != 8 or now.minute > 1:
        return

    y, m, d = now.year, now.month, now.day
    try:
        resp = httpx.get(
            f"https://isdayoff.ru/api/getdata?year={y}&month={m:02d}&day={d:02d}",
            timeout=10
        )
        code = resp.text.strip()
    except Exception:
        return

    weekday = now.strftime("%A")
    weekdays_ru = {
        "Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда",
        "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"
    }
    day_name = weekdays_ru.get(weekday, weekday)
    date_str = now.strftime("%d.%m.%Y")

    if code == "1":
        send_message(f"🌅 Доброе утро, Алексей!\n{day_name}, {date_str} — выходной день. Отдыхай!")
    elif code == "2":
        send_message(f"🌅 Доброе утро, Алексей!\n{day_name}, {date_str} — сокращённый рабочий день (предпраздничный). Уходим раньше!")
    else:
        send_message(f"🌅 Доброе утро, Алексей!\n{day_name}, {date_str} — рабочий день. Продуктивного дня!")


def make_greeting(item: dict, is_tomorrow: bool = False) -> str:
    desc = item["description"]
    year = item.get("year")
    now_year = datetime.now().year
    date = item["date"]

    def years_word(n):
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} год"
        elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
            return f"{n} года"
        else:
            return f"{n} лет"

    if year:
        years_passed = now_year - year
        if is_tomorrow:
            return f"⏰ Завтра ({date}): {desc} — будет {years_word(years_passed + 1)}! Не забудь подготовиться!"
        else:
            return f"🎉 Сегодня ({date}): {desc} — уже {years_word(years_passed)}!"
    else:
        if "новый год" in desc.lower():
            if is_tomorrow:
                return f"⏰ Завтра Новый {now_year + 1} год! Готовься к празднику! 🎄"
            else:
                return f"🎉 С Новым {now_year} годом, Алексей! Пусть этот год будет лучше предыдущего! 🥂"
        if "новогодняя ночь" in desc.lower():
            return f"🎄 Сегодня Новогодняя ночь! Готовься встречать {now_year + 1} год!"
        if is_tomorrow:
            return f"⏰ Завтра ({date}): {desc} — не забудь!"
        else:
            return f"🎉 Сегодня ({date}): {desc}! С праздником, Алексей!"


def check_calendar():
    """Проверяет календарные события в 9:00"""
    now = datetime.now()
    if now.hour != 9 or now.minute > 1:
        return

    today = now.strftime("%d.%m")
    tomorrow = (now + timedelta(days=1)).strftime("%d.%m")

    for item in get_dates_for_today():
        send_message(make_greeting(item, is_tomorrow=False))

    for item in get_dates_for_date(tomorrow):
        send_message(make_greeting(item, is_tomorrow=True))


print("Планировщик напоминаний запущен...")
while True:
    due = get_due_reminders()
    for reminder in due:
        print("Отправляю напоминание:", reminder)
        send_message("⏰ Напоминание: " + reminder)

    check_day_type()
    check_calendar()
    time.sleep(60)
