from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).parent
TASKS_PATH = BASE_DIR / "tasks.txt"
NOTES_PATH = BASE_DIR / "output" / "notes" / (datetime.now().strftime("%Y-%m-%d") + ".txt")
MEMORY_PATH = BASE_DIR / "memory.txt"
LOG_PATH = BASE_DIR / "logs" / "agent.log"

app = FastAPI()


def read_file(path: Path, default: str = "") -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default


@app.get("/", response_class=HTMLResponse)
def dashboard():
    tasks_raw = read_file(TASKS_PATH, "Задач нет.")
    tasks_lines = [l for l in tasks_raw.splitlines() if l.strip()]
    tasks_html = ""
    for line in tasks_lines:
        done = line.startswith("[x]")
        style = "text-decoration:line-through;color:#888;" if done else ""
        tasks_html += ">" + line + "</li>"

    notes_raw = read_file(NOTES_PATH, "Заметок сегодня нет.")
    notes_lines = [l for l in notes_raw.splitlines() if l.strip()]
    notes_html = "".join(">" + l + "</li>" for l in notes_lines) or ">Заметок сегодня нет.</li>"

    memory_raw = read_file(MEMORY_PATH, "Память пуста.").strip()
    memory_html = "".join("<p>" + l + "</p>" for l in memory_raw.splitlines()) or "<p>Память пуста.</p>"

    log_raw = read_file(LOG_PATH, "Лог пуст.")
    log_lines = log_raw.splitlines()[-30:]
    log_html = "".join("<div class='log-line'>" + l + "</div>" for l in reversed(log_lines))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>Danny Dashboard</title>
<style>
  body { font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; margin: 0; padding: 20px; }
  h1 { color: #00d4ff; text-align: center; margin-bottom: 5px; }
  .updated { text-align: center; color: #888; font-size: 12px; margin-bottom: 20px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .card { background: #16213e; border-radius: 10px; padding: 20px; border: 1px solid #0f3460; }
  .card.full { grid-column: 1 / -1; }
  h2 { color: #00d4ff; margin-top: 0; font-size: 16px; border-bottom: 1px solid #0f3460; padding-bottom: 8px; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { padding: 6px 0; border-bottom: 1px solid #0f3460; font-size: 14px; }
  li:last-child { border-bottom: none; }
  .log-line { font-size: 12px; font-family: monospace; padding: 3px 0; color: #aaa; border-bottom: 1px solid #0f3460; }
  .log-box { max-height: 300px; overflow-y: auto; }
  p { margin: 5px 0; font-size: 14px; }
</style>
</head>
<body>
<h1>Danny Dashboard</h1>
<div class="updated">Обновлено: """ + now + """ (авто-обновление каждые 30 сек)</div>
<div class="grid">
  <div class="card">
    <h2>Задачи</h2>
    <ul>""" + tasks_html + """</ul>
  </div>
  <div class="card">
    <h2>Заметки сегодня</h2>
    <ul>""" + notes_html + """</ul>
  </div>
  <div class="card">
    <h2>Долгосрочная память</h2>
    """ + memory_html + """
  </div>
  <div class="card">
    <h2>Напоминания</h2>
    <p>Смотри reminders.txt через агента</p>
  </div>
  <div class="card full">
    <h2>Лог действий (последние 30)</h2>
    <div class="log-box">""" + log_html + """</div>
  </div>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn, socket, time
    for i in range(10):
        try:
            s = socket.socket()
            s.bind(("0.0.0.0", 8012))
            s.close()
            break
        except OSError:
            print(f"[dashboard] Порт 8012 занят, жду 5 сек ({i+1}/10)...")
            time.sleep(5)
    uvicorn.run(app, host="0.0.0.0", port=8012, log_level="warning")
