from pathlib import Path
from tools.logger import log

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_PATH = BASE_DIR / "memory.txt"

CATEGORIES = [
    "[О пользователе]",
    "[Проекты]",
    "[Предпочтения]",
    "[Интересы]",
    "[Цели]",
    "[Разное]",
]


def load_memory() -> str:
    if not MEMORY_PATH.exists():
        return ""
    return MEMORY_PATH.read_text(encoding="utf-8").strip()


def add_memory(fact: str, category: str = "[Разное]") -> str:
    fact = fact.strip()
    if not fact:
        return "Нечего запоминать."

    content = load_memory()

    # Если категория есть — добавляем под неё
    if category in content:
        lines = content.splitlines()
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == category and not inserted:
                # Вставляем после заголовка категории
                new_lines.append(fact)
                inserted = True
        content = "\n".join(new_lines)
    else:
        # Категории нет — добавляем в конец с заголовком
        content = content + f"\n\n{category}\n{fact}"

    MEMORY_PATH.write_text(content.strip() + "\n", encoding="utf-8")
    log("memory", f"Запомнил [{category}]: {fact}")
    return f"Запомнил: {fact}"


def add_memory_simple(fact: str) -> str:
    """Быстрое добавление в [Разное] без указания категории."""
    return add_memory(fact, "[Разное]")


def get_profile_summary() -> str:
    """Возвращает краткий профиль для системного промпта Danny."""
    mem = load_memory()
    if not mem:
        return ""
    return mem


def clear_memory() -> str:
    MEMORY_PATH.write_text("", encoding="utf-8")
    return "Долгосрочная память очищена."


def auto_extract_and_save(user_text: str, llm_func) -> str:
    """
    Анализирует сообщение пользователя и автоматически
    запоминает важные факты без команды 'запомни'.
    """
    existing = load_memory()
    prompt = [
        {
            "role": "system",
            "content": (
                "Ты — система памяти AI-ассистента Danny. "
                "Проанализируй сообщение пользователя. "
                "Если в нём есть важный факт о пользователе (имя, город, работа, проект, предпочтение, цель, событие) — "
                "верни JSON: {\"save\": true, \"fact\": \"факт одной строкой\", \"category\": \"[О пользователе]|[Проекты]|[Предпочтения]|[Интересы]|[Цели]|[Разное]\"}\n"
                "Если ничего важного нет — верни: {\"save\": false}\n"
                "Уже известно:\n" + existing
            ),
        },
        {"role": "user", "content": user_text},
    ]
    try:
        import json
        raw = llm_func(prompt)
        data = json.loads(raw)
        if data.get("save") and data.get("fact"):
            return add_memory(data["fact"], data.get("category", "[Разное]"))
    except Exception:
        pass
    return ""
