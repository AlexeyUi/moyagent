from datetime import datetime
from uuid import uuid4
from pathlib import Path
import httpx
from agent_protocol import Agent as BaseAgent
from agent_protocol import StepRequestBody, Step
from tools.shell_run import run_safe_shell
from tools.files_write import safe_write_file
from tools.llm_openai import llm_simple_chat, llm_route_command, llm_ollama_chat, llm_smart_chat, detect_task_type
from tools.context_memory import add_message, get_history, clear_history
from tools.weather import get_weather
from tools.memory import load_memory, add_memory, clear_memory
from tools.reminders import add_reminder, list_reminders
from tools.logger import log
from tools.system_skills import get_status, start_service, stop_service
from tools.browser import browse_url, screenshot_url, google_search
from computer_skills import take_screenshot, click, double_click, type_text, press_key, scroll, get_screen_size, open_url_in_browser
from tools.research import search_and_summarize, read_and_summarize

BASE_DIR = Path(__file__).parent
NOTES_PATH = BASE_DIR / "notes.txt"
TASKS_PATH = BASE_DIR / "tasks.txt"


class Danny(BaseAgent):
    async def execute_step(self, step_request: StepRequestBody) -> Step:
        now = datetime.now().strftime("%H:%M")
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_input = step_request.input or ""
        user_input = raw_input.strip().lower()
        log("user", raw_input)

        def make_step(name, output, is_last=True):
            log("agent", output)
            return Step(
                task_id=step_request.task_id,
                step_id=str(uuid4()),
                name=name,
                input=raw_input,
                additional_input=step_request.additional_input or {},
                output=output,
                additional_output={},
                artifacts=[],
                is_last=is_last,
                status="completed",
            )

        if user_input.startswith("shell:"):
            cmd = raw_input.split(":", 1)[1].strip()
            return make_step("shell_step", run_safe_shell(cmd) if cmd else "Формат: shell: ls")

        if user_input.startswith("write:"):
            payload = raw_input.split(":", 1)[1].strip()
            if ":::" in payload:
                p, c = payload.split(":::", 1)
                return make_step("write_step", safe_write_file(p.strip(), c.lstrip()))
            return make_step("write_step", "Формат: write: путь ::: текст")

        if user_input.startswith("add_note"):
            note_text = raw_input.split(":", 1)[1].strip() if ":" in raw_input else ""
            if not note_text:
                return make_step("add_note_step", "Формат: add_note: текст")
            with NOTES_PATH.open("a", encoding="utf-8") as fh:
                fh.write(f"[{now}] {note_text}\n")
            return make_step("add_note_step", f"Заметка добавлена: {note_text}")

        if user_input in ("list_notes", "заметки", "показать заметки"):
            out = "Заметки:\n\n" + NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else "Заметок нет."
            return make_step("list_notes_step", out)

        if user_input in ("clear_notes", "очистить заметки"):
            NOTES_PATH.write_text("", encoding="utf-8")
            return make_step("clear_notes_step", "Заметки очищены.")

        if user_input.startswith("add_task"):
            payload = raw_input.split(":", 1)[1].strip() if ":" in raw_input else ""
            if not payload:
                return make_step("add_task_step", "Формат: add_task: текст | приоритет | дата")
            parts = [p.strip() for p in payload.split("|")]
            text = parts[0] if parts else ""
            priority = parts[1] if len(parts) > 1 else "normal"
            due = parts[2] if len(parts) > 2 else "без даты"
            with TASKS_PATH.open("a", encoding="utf-8") as fh:
                fh.write(f"[ ] {text} | p={priority} | due={due}\n")
            return make_step("add_task_step", f"Задача добавлена: {text} (приоритет: {priority}, дата: {due})")

        if user_input in ("list_tasks", "задачи", "показать задачи"):
            if TASKS_PATH.exists():
                lines = TASKS_PATH.read_text(encoding="utf-8").splitlines()
                out = "Задачи:\n\n" + "\n".join(f"{i+1}. {l}" for i, l in enumerate(lines)) if lines else "Список пуст."
            else:
                out = "tasks.txt не создан."
            return make_step("list_tasks_step", out)

        if user_input.startswith("done_task"):
            num_str = raw_input.split(":", 1)[1].strip() if ":" in raw_input else ""
            lines = TASKS_PATH.read_text(encoding="utf-8").splitlines() if TASKS_PATH.exists() else []
            try:
                idx = int(num_str)
                line = lines[idx - 1]
                lines[idx - 1] = "[x]" + line[3:] if line.startswith("[ ]") else "[x] " + line
                TASKS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
                out = f"Задача {idx} выполнена."
            except Exception as e:
                out = f"Ошибка: {e}"
            return make_step("done_task_step", out)

        if user_input in ("clear_tasks", "очистить задачи"):
            TASKS_PATH.write_text("", encoding="utf-8")
            return make_step("clear_tasks_step", "Задачи очищены.")

        if user_input in ("analyze_day", "анализ дня", "анализ задач"):
            if not TASKS_PATH.exists():
                return make_step("analyze_day_step", "Нет задач.")
            lines = TASKS_PATH.read_text(encoding="utf-8").splitlines()
            overdue, today_tasks, future, done = [], [], [], []
            for l in lines:
                if l.startswith("[x]"):
                    done.append(l)
                elif "due=" in l:
                    due = l.split("due=", 1)[1].strip()
                    if due < today_str:
                        overdue.append(l)
                    elif due == today_str:
                        today_tasks.append(l)
                    else:
                        future.append(l)
                else:
                    future.append(l)
            parts = ["Анализ задач:"]
            if overdue:
                parts += ["Просроченные:"] + [f"- {l}" for l in overdue]
            if today_tasks:
                parts += ["На сегодня:"] + [f"- {l}" for l in today_tasks]
            if future:
                parts += ["На потом:"] + [f"- {l}" for l in future]
            if done:
                parts += ["Сделано:"] + [f"- {l}" for l in done]
            return make_step("analyze_day_step", "\n".join(parts))

        if user_input.startswith("read_file"):
            path = raw_input.split(":", 1)[1].strip() if ":" in raw_input else ""
            if not path:
                return make_step("read_file_step", "Формат: read_file: путь")
            target = (BASE_DIR / path).resolve()
            if BASE_DIR not in target.parents and BASE_DIR != target:
                return make_step("read_file_step", "Нельзя читать файлы вне папки агента.")
            out = f"{path}:\n\n" + target.read_text(encoding="utf-8") if target.exists() else f"Файл не найден: {path}"
            return make_step("read_file_step", out)

        # Диспетчер LLM
        history = get_history()
        add_message("user", raw_input)
        route = llm_route_command(raw_input)
        log("debug", f"Route: {route}")
        cmd = route.get("command", "none")
        args = route.get("args", {}) or {}

        if cmd == "add_note":
            step_request.input = f"add_note: {args.get('text') or raw_input}"
            result = await self.execute_step(step_request)
            add_message("assistant", result.output)
            return result

        if cmd == "add_task":
            text = args.get("text") or raw_input
            priority = args.get("priority") or "normal"
            due = args.get("due") or "без даты"
            step_request.input = f"add_task: {text} | {priority} | {due}"
            result = await self.execute_step(step_request)
            add_message("assistant", result.output)
            return result

        if cmd == "list_tasks":
            step_request.input = "list_tasks"
            result = await self.execute_step(step_request)
            add_message("assistant", result.output)
            return result

        if cmd == "list_notes":
            step_request.input = "list_notes"
            result = await self.execute_step(step_request)
            add_message("assistant", result.output)
            return result

        if cmd == "analyze_day":
            step_request.input = "analyze_day"
            result = await self.execute_step(step_request)
            add_message("assistant", result.output)
            return result

        if cmd == "show_today_notes":
            f = BASE_DIR / "output" / "notes" / f"{today_str}.txt"
            out = f"Заметки за {today_str}:\n\n" + f.read_text(encoding="utf-8") if f.exists() else "Заметок за сегодня нет."
            add_message("assistant", out)
            return make_step("show_today_notes_step", out)

        if cmd == "shell":
            shell_cmd = args.get("cmd") or ""
            if shell_cmd:
                step_request.input = f"shell: {shell_cmd}"
                result = await self.execute_step(step_request)
                add_message("assistant", result.output)
                return result

        if cmd == "write":
            path = args.get("path") or ""
            content = args.get("content") or ""
            if path and content:
                step_request.input = f"write: {path} ::: {content}"
                result = await self.execute_step(step_request)
                add_message("assistant", result.output)
                return result

        if cmd == "done_task":
            num = args.get("number") or ""
            if num:
                step_request.input = f"done_task: {num}"
                result = await self.execute_step(step_request)
                add_message("assistant", result.output)
                return result

        if cmd == "get_weather":
            city = args.get("city") or "прокопьевск"
            try:
                weather_text = await get_weather(city)
                add_message("assistant", weather_text)
                return make_step("get_weather_step", weather_text)
            except Exception as e:
                return make_step("get_weather_step", f"Ошибка погоды: {e}")

        if cmd == "clear_history":
            clear_history()
            return make_step("clear_history_step", "История диалога очищена.")
        if cmd == "remember":
            fact = args.get("fact") or ""
            out = add_memory(fact) if fact else "Не понял что запомнить."
            add_message("assistant", out)
            return make_step("remember_step", out)

        if cmd == "show_memory":
            mem = load_memory()
            out = "Память:" + chr(10) + chr(10) + mem if mem else "Память пуста."
            add_message("assistant", out)
            return make_step("show_memory_step", out)

        if cmd == "add_reminder":
            time_str = args.get("time") or ""
            text = args.get("text") or ""
            out = add_reminder(time_str, text)
            add_message("assistant", out)
            return make_step("add_reminder_step", out)

        if cmd == "list_reminders":
            out = list_reminders()
            add_message("assistant", out)
            return make_step("list_reminders_step", out)

        if cmd == "clear_memory":
            out = clear_memory()
            add_message("assistant", out)
            return make_step("clear_memory_step", out)

        if cmd == "system_status":
            out = get_status()
            add_message("assistant", out)
            return make_step("system_status_step", out)

        if cmd == "start_service":
            name = args.get("name") or ""
            out = start_service(name) if name else "Укажи имя сервиса."
            add_message("assistant", out)
            return make_step("start_service_step", out)

        if cmd == "stop_service":
            name = args.get("name") or ""
            out = stop_service(name) if name else "Укажи имя сервиса."
            add_message("assistant", out)
            return make_step("stop_service_step", out)

        if cmd == "browse_url":
            url = args.get("url") or ""
            if url:
                out = await browse_url(url)
                out_short = out[:2000] + ("..." if len(out) > 2000 else "")
                add_message("assistant", out_short)
                return make_step("browse_url_step", out_short)
            return make_step("browse_url_step", "Укажи url.")

        if cmd == "screenshot_url":
            url = args.get("url") or ""
            if url:
                out = await screenshot_url(url)
                add_message("assistant", out)
                return make_step("screenshot_url_step", out)
            return make_step("screenshot_url_step", "Укажи url.")

        if cmd == "google_search":
            query = args.get("query") or ""
            if query:
                out = await google_search(query)
                out_short = out[:2000] + ("..." if len(out) > 2000 else "")
                add_message("assistant", out_short)
                return make_step("google_search_step", out_short)
            return make_step("google_search_step", "Укажи запрос.")
        if cmd == "take_screenshot":
            img_b64 = take_screenshot()
            return make_step("take_screenshot_step", f"[SCREENSHOT:{img_b64}]")

        if cmd == "click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            button = args.get("button", "left")
            out = click(x, y, button)
            return make_step("click_step", out)

        if cmd == "double_click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            out = double_click(x, y)
            return make_step("double_click_step", out)

        if cmd == "type_text":
            text_to_type = args.get("text", "")
            out = type_text(text_to_type)
            return make_step("type_text_step", out)

        if cmd == "press_key":
            key = args.get("key", "")
            out = press_key(key)
            return make_step("press_key_step", out)

        if cmd == "scroll":
            x = int(args.get("x", 960))
            y = int(args.get("y", 540))
            direction = args.get("direction", "down")
            amount = int(args.get("amount", 3))
            out = scroll(x, y, direction, amount)
            return make_step("scroll_step", out)

        if cmd == "open_url":
            url = args.get("url", "")
            out = open_url_in_browser(url)
            return make_step("open_url_step", out)

        if cmd == "get_screen_size":
            out = str(get_screen_size())
            return make_step("get_screen_size_step", out)


        if cmd == "click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            button = args.get("button", "left")
            out = click(x, y, button)
            return make_step("click_step", out)

        if cmd == "double_click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            out = double_click(x, y)
            return make_step("double_click_step", out)

        if cmd == "type_text":
            text = args.get("text", "")
            out = type_text(text)
            return make_step("type_text_step", out)

        if cmd == "press_key":
            key = args.get("key", "")
            out = press_key(key)
            return make_step("press_key_step", out)

        if cmd == "scroll":
            x = int(args.get("x", 960))
            y = int(args.get("y", 540))
            direction = args.get("direction", "down")
            amount = int(args.get("amount", 3))
            out = scroll(x, y, direction, amount)
            return make_step("scroll_step", out)

        if cmd == "open_url":
            url = args.get("url", "")
            out = open_url_in_browser(url)
            return make_step("open_url_step", out)

        if cmd == "get_screen_size":
            out = str(get_screen_size())
            return make_step("get_screen_size_step", out)



        if cmd == "click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            button = args.get("button", "left")
            out = click(x, y, button)
            return make_step("click_step", out)

        if cmd == "double_click":
            x = int(args.get("x", 0))
            y = int(args.get("y", 0))
            out = double_click(x, y)
            return make_step("double_click_step", out)

        if cmd == "type_text":
            text = args.get("text", "")
            out = type_text(text)
            return make_step("type_text_step", out)

        if cmd == "press_key":
            key = args.get("key", "")
            out = press_key(key)
            return make_step("press_key_step", out)

        if cmd == "scroll":
            x = int(args.get("x", 960))
            y = int(args.get("y", 540))
            direction = args.get("direction", "down")
            amount = int(args.get("amount", 3))
            out = scroll(x, y, direction, amount)
            return make_step("scroll_step", out)

        if cmd == "open_url":
            url = args.get("url", "")
            out = open_url_in_browser(url)
            return make_step("open_url_step", out)

        if cmd == "research":
            query = args.get("query") or ""
            if query:
                out = await search_and_summarize(query, llm_simple_chat)
                out_short = out[:3500] + ("..." if len(out) > 3500 else "")
                add_message("assistant", out_short[:500])
                return make_step("research_step", out_short)
            return make_step("research_step", "Укажи тему для исследования.")

        if cmd == "write_content":
            content_type = args.get("type") or "текст"
            topic = args.get("topic") or ""
            if not topic:
                return make_step("write_content_step", "Укажи тему.")
            memory = load_memory()
            system = "Ты профессиональный копирайтер Danny. Пиши по-русски."
            if memory:
                system += " Контекст о пользователе: " + memory
            prompts = {
                "пост": "Напиши пост для соцсетей на тему: " + topic + ". 3-5 предложений, цепляющий заголовок, призыв к действию.",
                "описание": "Напиши описание товара/услуги: " + topic + ". 5-7 предложений, выгоды, характеристики.",
                "заявка": "Напиши заявку на фриланс-проект: " + topic + ". Коротко, профессионально.",
                "ответ": "Напиши вежливый ответ клиенту: " + topic + ". Кратко, по делу.",
                "письмо": "Напиши деловое письмо на тему: " + topic + ". Профессиональный тон.",
            }
            user_prompt = prompts.get(content_type, "Напиши " + content_type + " на тему: " + topic)
            prompt = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ]
            try:
                out = llm_simple_chat(prompt)
                add_message("assistant", out)
                return make_step("write_content_step", out)
            except Exception as e:
                return make_step("write_content_step", "Ошибка: " + str(e))

        if cmd == "read_page":
            url = args.get("url") or ""
            question = args.get("question") or "Сделай краткую выжимку главного содержимого"
            if url:
                out = await read_and_summarize(url, question, llm_simple_chat)
                out_short = out[:3500] + ("..." if len(out) > 3500 else "")
                add_message("assistant", out_short[:500])
                return make_step("read_page_step", out_short)
            return make_step("read_page_step", "Укажи url страницы.")


        memory = load_memory()
        system_content = (
            "Ты — Danny, персональный AI-ассистент Алексея. "
            "Твой стиль: умный, живой, дружеский — как Джарвис у Тони Старка. "
            "Ты знаешь своего хозяина, помнишь контекст, думаешь наперёд. "
            "Отвечай кратко и по делу, на русском. Без воды и официоза."
        )
        if memory:
            system_content += chr(10) + chr(10) + "Что ты знаешь об Алексее:" + chr(10) + memory
        
        # Автозапоминание — Danny сам замечает важное
        try:
            from tools.memory import auto_extract_and_save
            auto_extract_and_save(raw_input, llm_simple_chat)
        except Exception:
            pass

        prompt = [{"role": "system", "content": system_content}] + history + [{"role": "user", "content": raw_input}]
        try:
            task_type = detect_task_type(raw_input)
            answer = llm_smart_chat(prompt, task_type=task_type)
            add_message("assistant", answer)
            return make_step("llm_fallback", answer)
        except Exception as e:
            return make_step("llm_fallback", f"Ошибка LLM: {e}")
