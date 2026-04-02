from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "logs" / "agent.log"


def log(role: str, text: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[" + now + "] " + role.upper() + ": " + text.replace("\n", " ") + "\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
