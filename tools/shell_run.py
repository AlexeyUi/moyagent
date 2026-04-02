import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_BINARIES = {"ls", "cat", "pwd", "echo", "head", "tail"}


def run_safe_shell(command: str) -> str:
    command = command.strip()
    if not command:
        return "Пустая команда."

    if any(x in command for x in ["..", ";", "|", "&&", "||", ">", "<", "$(", "`"]):
        return "Команда отклонена: недопустимые символы или конструкции."

    parts = command.split()
    binary = parts[0]

    if binary not in ALLOWED_BINARIES:
        return f"Команда '{binary}' не разрешена. Доступны: {', '.join(sorted(ALLOWED_BINARIES))}"

    try:
        result = subprocess.run(
            parts,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        return f"Ошибка выполнения команды: {e!r}"

    out = result.stdout.strip()
    err = result.stderr.strip()

    if result.returncode != 0:
        return f"Команда завершилась с кодом {result.returncode}.\nSTDOUT:\n{out}\nSTDERR:\n{err}"

    return out or "(пустой вывод)"

