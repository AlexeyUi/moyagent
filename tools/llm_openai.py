import json
import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = "YOUR_OPENAI_API_KEY_HERE-Ob95zGRO1SUR_F2rOtHSo9LbjuWwG3jm6W7emhMPHWMDsV_1IDCkkfAXpdJkNdJZ9PG5dhBwIST3BlbkFJLWXtYeA0CEnS_PmPud14iLRUPiFAj6oH2U4aGnVtxA_cx0jy4LWDHb14cGLeKANIm4Ln8coWkA"
client = OpenAI(timeout=60.0, api_key=api_key)


def llm_simple_chat(messages: List[Dict[str, str]], model: str = "gpt-4.1-mini") -> str:
    """Простой вызов OpenAI Chat."""
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""


def llm_route_command(user_text: str, history: List[Dict[str, str]] = None) -> dict:
    """
    Определяет команду по тексту пользователя.
    Возвращает dict: {"command": "...", "args": {...}}
    """
    today = __import__('datetime').date.today().isoformat()
    import datetime
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    system = {
        "role": "system",
        "content": (
            "Ты — маршрутизатор команд для агента Danny.\n"
            "Всегда отвечай ТОЛЬКО валидным JSON без пояснений.\n\n"
            "Доступные команды:\n"
            "- add_task: добавить задачу. args: {\"text\": \"...\", \"priority\": \"normal|high|low\", \"due\": \"YYYY-MM-DD\"}\n"
            "- add_note: добавить заметку. args: {\"text\": \"...\"}\n"
            "- list_tasks: показать все задачи. args: {}\n"
            "- list_notes: показать все заметки. args: {}\n"
            "- analyze_day: анализ задач на сегодня. args: {}\n"
            "- show_today_notes: показать заметки за сегодня. args: {}\n"
            "- shell: выполнить команду. args: {\"cmd\": \"ls|cat|pwd|head|tail ...\"}\n"
            "- write: записать текст в файл. args: {\"path\": \"путь.txt\", \"content\": \"текст\"}\n"
            "- done_task: отметить задачу выполненной. args: {\"number\": \"1\"}\n"
            "- get_weather: узнать погоду в городе. args: {\"city\": \"название города\"}\n"
            "- clear_history: очистить историю диалога. args: {}\n"
            "- add_reminder: добавить напоминание. args: {\"time\": \"HH:MM\", \"text\": \"...\"}\"\n"
            "- list_reminders: показать напоминания. args: {}\n"
            "- system_status: узнать статус сервисов агента. args: {}\n"
            "- start_service: запустить сервис. args: {\"name\": \"агент|бот|дашборд|напоминания\"}\n"
            "- stop_service: остановить сервис. args: {\"name\": \"агент|бот|дашборд|напоминания\"}\n"
            "- browse_url: открыть страницу и прочитать текст. args: {\"url\": \"https://...\"}\n"
            "- screenshot_url: сделать скриншот страницы. args: {\"url\": \"https://...\"}\n"
            "- google_search: ТОЛЬКО быстрый список заголовков, без анализа. args: {\"query\": \"запрос\"}\n"
            "- research: найти И проанализировать — используй когда просят найди, исследуй, узнай, что такое. args: {\"query\": \"тема\"}\n"
            "- write_content: написать контент. args: {\"type\": \"пост|описание|заявка|ответ|письмо\", \"topic\": \"тема\"}\n"
            "- read_page: прочитать страницу и ответить на вопрос. args: {\"url\": \"https://...\", \"question\": \"вопрос или задача\"}\n"
            "- remember: запомнить факт о пользователе. args: {\"fact\": \"...\"}\n"
            "- show_memory: показать долгосрочную память. args: {}\n"
            "- clear_memory: очистить долгосрочную память. args: {}\n"
            "- take_screenshot: сделать скриншот виртуального экрана. args: {}\n"
            "- open_url: открыть сайт в браузере на виртуальном экране. args: {\"url\": \"https://...\"}\n"
            "- click: кликнуть мышью по координатам x,y. args: {\"x\": 100, \"y\": 200}\n"
            "- type_text: ввести текст с клавиатуры. args: {\"text\": \"...\"}\n"
            "- press_key: нажать клавишу. args: {\"key\": \"enter\"}\n"
            "- scroll: прокрутить экран. args: {\"direction\": \"down\", \"amount\": 3}\n"
            "ВАЖНО: слова скриншот/снимок/скрин/сфотографируй экран = команда take_screenshot. НЕ open_url, НЕ shell.\n"
            "- none: просто ответить на вопрос. args: {}\n\n"
            f"Сегодня: {today}, завтра: {tomorrow}.\n"
            "Если пользователь говорит 'сегодня' — подставь реальную дату.\n"
            "Если пользователь говорит 'завтра' — подставь дату +1 день.\n"
            "В поле text пиши ТОЛЬКО суть задачи/заметки, без слов 'добавь', 'запиши' и т.п.\n"
            "ВАЖНО: если пользователь говорит найди/исследуй/узнай/расскажи о теме — ВСЕГДА используй research, НЕ google_search.\n"
            "ВАЖНО: если пользователь спрашивает что ты знаешь о нём, кто он, расскажи о себе/обо мне — используй none, Danny сам ответит своими словами используя память.\n"
            "ВАЖНО: если пользователь просит сделать скриншот экрана/снимок/скрин — ВСЕГДА используй take_screenshot, НЕ shell.\n"
            "ВАЖНО: если пользователь просит открыть сайт в браузере — используй open_url.\n"
            "ВАЖНО: если пользователь просит кликнуть/нажать/ввести текст на экране — используй click/type_text/press_key.\n"
            "Пример: {\"command\": \"add_task\", \"args\": {\"text\": \"купить хлеб\", \"priority\": \"normal\", \"due\": \"" + today + "\"}}"
        ),
    }

    # Собираем сообщения: system + история + текущий запрос
    messages = [system]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except Exception:
        return {"command": "none", "args": {}}


def llm_ollama_chat(messages: list, model: str = "mistral") -> str:
    """Локальный чат через Ollama (бесплатно, офлайн)."""
    import httpx, json
    try:
        resp = httpx.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60.0
        )
        return resp.json().get("message", {}).get("content", "")
    except Exception as e:
        # Если Ollama недоступна — fallback на OpenAI
        return llm_simple_chat(messages)



def llm_smart_chat(messages: list, task_type: str = "chat") -> str:
    """
    Умный роутер — выбирает модель по типу задачи.
    
    task_type:
      "chat"     → Mistral 7B (обычный разговор, быстро, бесплатно)
      "code"     → CodeLlama 7B (написание и анализ кода)
      "fast"     → Llama 3.2 (быстрые короткие задачи)
      "think"    → DeepSeek-R1 (глубокий анализ, сложные задачи)
      "web"      → GPT-4.1-mini (нужен интернет или сложный анализ)
    """
    import httpx

    model_map = {
        "chat":  ("ollama", "mistral"),
        "code":  ("ollama", "codellama"),
        "fast":  ("ollama", "llama3.2"),
        "think": ("ollama", "deepseek-r1:7b"),
        "web":   ("openai", "gpt-4.1-mini"),
    }

    backend, model = model_map.get(task_type, ("ollama", "mistral"))

    if backend == "ollama":
        try:
            resp = httpx.post(
                "http://localhost:11434/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=120.0
            )
            result = resp.json().get("message", {}).get("content", "")
            if result:
                return result
        except Exception:
            pass
        # Fallback на OpenAI если Ollama недоступна
        return llm_simple_chat(messages)

    else:
        return llm_simple_chat(messages)


def detect_task_type(user_text: str) -> str:
    """Определяет тип задачи по тексту для выбора модели."""
    text = user_text.lower()
    
    # Код
    code_keywords = ["код", "напиши функцию", "python", "скрипт", "программ", 
                     "class", "def ", "баг", "ошибка в коде", "codellama"]
    if any(k in text for k in code_keywords):
        return "code"
    
    # Глубокий анализ
    think_keywords = ["проанализируй", "объясни подробно", "почему", "разбери", 
                      "думай", "сравни", "плюсы и минусы", "deepseek"]
    if any(k in text for k in think_keywords):
        return "think"
    
    # Быстрые задачи (задачи, заметки — но они обычно не доходят до чата)
    fast_keywords = ["быстро", "кратко", "одним словом", "да или нет"]
    if any(k in text for k in fast_keywords):
        return "fast"
    
    # По умолчанию — обычный чат через Mistral
    return "chat"

