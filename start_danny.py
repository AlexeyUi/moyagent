#!/usr/bin/env python3
import subprocess, time, os, sys, threading, pathlib

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

# Xvfb
if not pathlib.Path("/tmp/.X99-lock").exists():
    subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1920x1080x24"])
    time.sleep(2)
os.environ["DISPLAY"] = ":99"
print("[danny] Xvfb OK")

# Агент API
subprocess.Popen([PYTHON, "-m", "uvicorn", "ap_agent:app", "--host", "0.0.0.0", "--port", "8011"], cwd=BASE)
time.sleep(3)
print("[danny] Агент запущен: http://localhost:8011")

# Напоминания
subprocess.Popen([PYTHON, "reminder_bot.py"], cwd=BASE)
print("[danny] Напоминания запущены")

# Telegram бот — запускаем последним, БЕЗ restart loop
time.sleep(2)
print("[danny] Запускаю Telegram бот...")
bot = subprocess.Popen([PYTHON, "telegram_bot.py"], cwd=BASE)

print("[danny] Danny запущен! Ctrl+C для остановки")
print("[danny] Агент: http://localhost:8011")

try:
    bot.wait()
except KeyboardInterrupt:
    print("[danny] Остановка...")
    bot.terminate()
