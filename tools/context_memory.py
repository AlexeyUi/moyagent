from collections import deque
from typing import List, Dict

# Храним последние 10 сообщений в памяти процесса
MAX_HISTORY = 10
_history: deque = deque(maxlen=MAX_HISTORY)


def add_message(role: str, content: str) -> None:
    """Добавить сообщение в историю. role: 'user' или 'assistant'"""
    _history.append({"role": role, "content": content})


def get_history() -> List[Dict[str, str]]:
    """Вернуть список сообщений для передачи в LLM."""
    return list(_history)


def clear_history() -> None:
    """Очистить историю диалога."""
    _history.clear()
