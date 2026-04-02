#!/usr/bin/env python3
import subprocess, time, os, signal, sys, threading, pathlib, socket

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable
processes = []

def cleanup(sig=None, frame=None):
    print("[start_all] Остановка...")
    for p in processes:
        try: p.terminate()
        except: pass
    time.sleep(2)
    for p in processes:
        try: p.kill()
        except: pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) != 0

def wait_port_free(port, timeout=60):
    print(f"[start_all] Жду освобождения порта {port}...")
    for _ in range(timeout):
        if port_free(port):
            print(f"[start_all] Порт {port} свободен.")
            return True
        time.sleep(1)
    print(f"[start_all] ВНИМАНИЕ: порт {port} всё ещё занят!")
    return False

# Убиваем старые процессы
print("[start_all] Убиваю старые процессы...")
os.system("pkill -9 -f telegram_bot.py 2>/dev/null")
os.system("pkill -9 -f 'uvicorn ap_agent' 2>/dev/null")
os.system("pkill -9 -f reminder_bot 2>/dev/null")
os.system("fuser -k 8011/tcp 2>/dev/null")
time.sleep(3)

# Ждём освобождения порта (макс 60 сек)
wait_port_free(8011)

# Ждём освобождения Telegram сессии
print("[start_all] Жду 35 сек чтобы Telegram отпустил сессию...")
time.sleep(35)

# Xvfb
if not pathlib.Path("/tmp/.X99-lock").exists():
    p = subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1920x1080x24"])
    processes.append(p)
    time.sleep(2)
    print("[start_all] Xvfb запущен")
else:
    print("[start_all] Xvfb уже работает")
os.environ["DISPLAY"] = ":99"

def run_loop(name, cmd, restart_delay=15):
    env = os.environ.copy()
    while True:
        try:
            print(f"[start_all] Запускаю {name}...")
            proc = subprocess.Popen(cmd, cwd=BASE, env=env)
            processes.append(proc)
            proc.wait()
            code = proc.returncode
            print(f"[start_all] {name} завершился (код {code}), перезапускаю через {restart_delay} сек...")
        except Exception as e:
            print(f"[start_all] Ошибка {name}: {e}")
        time.sleep(restart_delay)

components = [
    ("Агент (API)",  [PYTHON, "-m", "uvicorn", "ap_agent:app", "--host", "0.0.0.0", "--port", "8011"], 15),
    ("Telegram бот", [PYTHON, "telegram_bot.py"], 40),
    ("Напоминания",  [PYTHON, "reminder_bot.py"], 15),
]

for name, cmd, delay in components:
    t = threading.Thread(target=run_loop, args=(name, cmd, delay), daemon=True)
    t.start()
    time.sleep(4)

print("[start_all] Все компоненты Danny запущены.")
print("[start_all] Агент: http://localhost:8011")
print("[start_all] Ctrl+C для остановки")

while True:
    time.sleep(30)
