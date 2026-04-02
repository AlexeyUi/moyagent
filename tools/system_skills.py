import subprocess
import shlex
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_SERVICES = {
    "агент": [
        "uvicorn", "ap_agent:app",
        "--host", "0.0.0.0",
        "--port", "8011",
        "--reload"
    ],
    "дашборд": [
        "uvicorn", "dashboard:app",
        "--host", "0.0.0.0",
        "--port", "8080",
        "--reload"
    ],
    "бот": ["python3", "telegram_bot.py"],
    "напоминания": ["python3", "reminder_bot.py"],
}


def get_status() -> str:
    lines = []
    for name, cmd in ALLOWED_SERVICES.items():
        binary = cmd[0]
        arg = cmd[1] if len(cmd) > 1 else ""
        try:
            result = subprocess.run(
                ["pgrep", "-f", arg or binary],
                capture_output=True, text=True
            )
            status = "запущен" if result.stdout.strip() else "остановлен"
        except Exception:
            status = "неизвестно"
        lines.append(name + ": " + status)
    return "Статус сервисов:\n\n" + "\n".join(lines)


def start_service(name: str) -> str:
    name = name.strip().lower()
    if name not in ALLOWED_SERVICES:
        available = ", ".join(ALLOWED_SERVICES.keys())
        return "Неизвестный сервис: " + name + ". Доступны: " + available
    cmd = ALLOWED_SERVICES[name]
    try:
        subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return "Сервис " + name + " запускается..."
    except Exception as e:
        return "Ошибка запуска " + name + ": " + str(e)


def stop_service(name: str) -> str:
    name = name.strip().lower()
    if name not in ALLOWED_SERVICES:
        available = ", ".join(ALLOWED_SERVICES.keys())
        return "Неизвестный сервис: " + name + ". Доступны: " + available
    cmd = ALLOWED_SERVICES[name]
    arg = cmd[1] if len(cmd) > 1 else cmd[0]
    try:
        subprocess.run(["pkill", "-f", arg], capture_output=True)
        return "Сервис " + name + " остановлен."
    except Exception as e:
        return "Ошибка остановки " + name + ": " + str(e)
