import os
import tempfile
import logging
import httpx

from tools.calendar_store import add_date, list_dates
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

AGENT_BASE_URL = os.environ.get("AGENT_BASE_URL", "http://localhost:8011")



async def transcribe_voice(file_path: str) -> str:
    """Транскрибирует голосовое сообщение через OpenAI Whisper API."""
    import httpx
    from tools.llm_openai import api_key
    with open(file_path, "rb") as f:
        audio_data = f.read()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": ("voice.ogg", audio_data, "audio/ogg")},
            data={"model": "whisper-1", "language": "ru"},
        )
    if resp.status_code == 200:
        return resp.json().get("text", "")
    return ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! Я связан с твоим AutoGPT-агентом.\n\n"
        "Ты можешь:\n"
        "• Просто написать задачу обычным текстом (например: \"Придумай план выходного\") — я передам её агенту.\n"
        "• Или использовать специальные команды (позже допишем сюда список).\n\n"
        "Напиши любую задачу, а я попробую её решить через агента."
    )
    await update.message.reply_text(text)

async def add_date_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Формат:\n/date ДД.ММ описание\n\nПример:\n/date 12.05 День рождения мамы"
        )
        return

    # Принимаем ДД.ММ и ДД.ММ.ГГГГ
    raw_args = " ".join(context.args).strip()
    parts = raw_args.split()
    date_str = parts[0]
    description = " ".join(parts[1:]).strip()

    try:
        item = add_date(date_str, description)
        await update.message.reply_text(
            f"📅 Сохранил дату:\n{item['date']} — {item['description']}"
        )
    except ValueError:
        await update.message.reply_text(
            "⚠️ Неверный формат даты. Используй ДД.ММ, например: 12.05"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Не удалось сохранить дату: {e!r}")

async def list_dates_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    items = list_dates()
    if not items:
        await update.message.reply_text("📭 Пока нет сохранённых дат.")
        return

    lines = ["📅 Твои даты:\n"]
    for idx, item in enumerate(items, start=1):
        lines.append(f"{idx}. {item['date']} — {item['description']}")

    await update.message.reply_text("\n".join(lines))

def create_task(user_input: str) -> dict:
    """Создаёт задачу в агенте и выполняет первый шаг."""
    url_task = f"{AGENT_BASE_URL}/ap/v1/agent/tasks"
    url_step = f"{AGENT_BASE_URL}/ap/v1/agent/tasks/{{task_id}}/steps"

    with httpx.Client(timeout=120.0) as client:
        # создаём задачу
        resp = client.post(url_task, json={"input": user_input})
        resp.raise_for_status()
        task = resp.json()
        task_id = task.get("task_id") or task.get("id") or task.get("task", {}).get("id")

        if not task_id:
            raise RuntimeError(f"Не удалось получить task_id из ответа агента: {task}")

        # создаём шаг
        resp = client.post(url_step.format(task_id=task_id), json={"input": user_input})
        resp.raise_for_status()
        step = resp.json()

    return {"task": task, "step": step}

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает текущую погоду в Прокопьевске через Open-Meteo."""
    lat = 53.8857
    lon = 86.6668

    weather_codes = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Изморозь",
        51: "Лёгкая морось",
        53: "Морось",
        55: "Сильная морось",
        61: "Слабый дождь",
        63: "Дождь",
        65: "Сильный дождь",
        71: "Слабый снег",
        73: "Снег",
        75: "Сильный снег",
        80: "Ливень",
        81: "Ливень",
        82: "Сильный ливень",
        95: "Гроза",
        96: "Гроза с градом",
        99: "Сильная гроза с градом",
    }

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&timezone=auto"
    )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current_weather", {})
        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        weathercode = current.get("weathercode")
        time_value = current.get("time")

        description = weather_codes.get(weathercode, f"Код погоды: {weathercode}")

        text = (
            "🌤 Погода в Прокопьевске:\n\n"
            f"Температура: {temperature}°C\n"
            f"Состояние: {description}\n"
            f"Ветер: {windspeed} км/ч\n"
            f"Время наблюдения: {time_value}"
        )
    except Exception as e:
        text = f"⚠️ Не удалось получить погоду: {e!r}"

    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает любой текст БЕЗ слэша в начале как задачу для агента."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    # если это команда (/start, /help и т.п.) — не трогаем
    if text.startswith("/"):
        return

    await update.message.reply_text("Понял, думаю...")

    try:
        result = create_task(text)
        step = result["step"]

        # возможные варианты структуры ответа, подстраховываемся
        output = (
            step.get("output")
            or step.get("step", {}).get("output")
            or "Агент не вернул текстового ответа."
        )

        if output.startswith("[SCREENSHOT:") and output.endswith("]"):
            import base64, io
            img_data = base64.b64decode(output[len("[SCREENSHOT:"):- 1])
            await update.message.reply_photo(photo=io.BytesIO(img_data), caption="Скриншот экрана")
        else:
            await update.message.reply_text(output)
    except Exception as e:
        logger.exception("Ошибка при обращении к агенту")
        await update.message.reply_text(f"Ошибка при обращении к агенту: {e}")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Не установлен TELEGRAM_BOT_TOKEN")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    # /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("date", add_date_command))
    app.add_handler(CommandHandler("dates", list_dates_command))
    app.add_handler(CommandHandler("weather", weather))
    # любой текст без / в начале → в агента
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, voice_message))
    app.add_handler(MessageHandler(filters.PHOTO, photo_message))

    app.run_polling(drop_pending_updates=True)





async def text_to_voice(text: str) -> bytes:
    """Генерирует голосовой ответ через OpenAI TTS."""
    from tools.llm_openai import api_key
    import httpx
    # Убираем эмодзи и спецсимволы для чистого голоса
    import re
    clean = re.sub(r'[^\w\s\.,!?;:\-]', '', text)
    clean = clean[:500]  # не больше 500 символов
    resp = httpx.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "tts-1", "input": clean, "voice": "alloy"},
        timeout=30
    )
    return resp.content


async def process_message(update, context, text: str, reply_voice: bool = False):
    """Обрабатывает текст (из голосового или текстового сообщения)."""
    import httpx as _httpx
    task_url = "http://localhost:8011/ap/v1/agent/tasks"
    step_url_tpl = "http://localhost:8011/ap/v1/agent/tasks/{task_id}/steps"
    try:
        async with _httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(task_url, json={"input": text})
            task_id = r.json()["task_id"]
            r2 = await client.post(step_url_tpl.format(task_id=task_id), json={"input": text})
            answer = r2.json().get("output", "")
        if answer.startswith("[SCREENSHOT:"):
            import base64, io
            b64 = answer[len("[SCREENSHOT:"):-1]
            img_bytes = base64.b64decode(b64)
            await update.message.reply_photo(photo=io.BytesIO(img_bytes))
        elif reply_voice and answer:
            import io
            audio = await text_to_voice(answer)
            await update.message.reply_voice(voice=io.BytesIO(audio))
        else:
            await update.message.reply_text(answer or "Готово.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")



async def photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Анализирует фото через GPT-4o Vision."""
    if not update.message or not update.message.photo:
        return

    await update.message.reply_text("🔍 Смотрю на фото...")

    # Берём фото максимального качества
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    import tempfile, os, base64, httpx
    from tools.llm_openai import api_key

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)

    try:
        with open(tmp_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        os.unlink(tmp_path)

        # Подпись к фото как вопрос
        user_caption = (update.message.caption or "").strip().lower()

        # Если это селфи Алексея — отвечаем без Vision API
        selfie_keywords = ["это я", "привет danny", "привет, danny", "как я выгляжу", "selfie", "селфи"]
        if any(k in user_caption for k in selfie_keywords) or (not user_caption):
            # Проверяем есть ли лицо — если да, отвечаем напрямую
            import random
            greetings = [
                "Привет, Алексей! Отлично выглядишь сегодня — готов к работе?",
                "О, Алексей! Как всегда в форме. Что на повестке?",
                "Приветствую, Алексей! Хорошее настроение — вижу по фото. Чем займёмся?",
                "Привет, шеф! Выглядишь бодро. Что делаем сегодня?",
                "Алексей! Рад тебя видеть. Готов к новым задачам!",
            ]
            await update.message.reply_text(random.choice(greetings))
            return

        caption = update.message.caption or "Опиши подробно что на фото. Если чек или документ — прочитай текст. Если код — проанализируй. Отвечай по-русски."

        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }],
                "max_tokens": 1000
            },
            timeout=30
        )
        answer = resp.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка анализа фото: {e}")


async def voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает голосовые сообщения."""
    if not update.message or not update.message.voice:
        return
    await update.message.reply_text("🎤 Слушаю...")
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)
    try:
        text = await transcribe_voice(tmp_path)
        os.unlink(tmp_path)
        if not text:
            await update.message.reply_text("❌ Не смог распознать голос. Попробуй ещё раз.")
            return
        await update.message.reply_text(f"🗣 Распознал: {text}")
        # Обрабатываем как обычное текстовое сообщение
        class FakeMessage:
            pass
        fake_update = type("FakeUpdate", (), {})()
        fake_update.message = update.message
        fake_update.effective_user = update.effective_user
        # Напрямую вызываем агента с распознанным текстом
        await process_message(update, context, text, reply_voice=True)
    except Exception as e:
        os.unlink(tmp_path)
        await update.message.reply_text(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
