from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_inside_base(relative_path: str) -> Path:
    rel = relative_path.strip()
    if not rel:
        raise ValueError("Путь к файлу пуст.")

    target = (BASE_DIR / rel).resolve()

    try:
        target.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError("Нельзя писать файлы вне папки агента.")

    return target


def safe_write_file(relative_path: str, content: str) -> str:
    try:
        target = _resolve_inside_base(relative_path)
    except ValueError as e:
        return f"Ошибка пути: {e}"

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except Exception as e:
        return f"Не удалось записать файл: {e!r}"

    return f"Файл перезаписан: {target.relative_to(BASE_DIR)}"

