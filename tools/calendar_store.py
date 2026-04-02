import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "output"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CALENDAR_PATH = DATA_DIR / "calendar_dates.json"


def load_dates() -> list:
    if not CALENDAR_PATH.exists():
        return []
    try:
        return json.loads(CALENDAR_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_dates(items: list) -> None:
    CALENDAR_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_date(date_str: str, description: str) -> dict:
    # Принимаем ДД.ММ и ДД.ММ.ГГГГ — сохраняем только ДД.ММ
    date_str = date_str.strip()
    if len(date_str.split(".")) == 3:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        date_str = dt.strftime("%d.%m")
    else:
        datetime.strptime(date_str, "%d.%m")  # проверка формата
    items = load_dates()
    item = {
        "date": date_str,
        "description": description.strip(),
    }
    items.append(item)
    save_dates(items)
    return item


def list_dates() -> list:
    return load_dates()


def get_dates_for_today() -> list:
    """Возвращает события на сегодня."""
    today = datetime.now().strftime("%d.%m")
    return [i for i in load_dates() if i.get("date") == today]


def get_dates_for_date(date_str: str) -> list:
    """Возвращает события на конкретную дату ДД.ММ."""
    return [i for i in load_dates() if i.get("date") == date_str]
