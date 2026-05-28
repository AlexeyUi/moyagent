# MoyAgent

MoyAgent is my first AI-agent prototype. It was built on top of AutoGPT /
Forge as a practical learning project and later evolved into
[Danny_Core](https://github.com/AlexeyUi/Danny_Core), my own AI assistant
platform.

This repository is kept as a working prototype and portfolio artifact, not as a
production product.

## Status

Archived working prototype / learning project.

MoyAgent demonstrates the first version of the ideas that later became
Danny_Core: a Telegram-facing assistant with memory, tools, voice, vision,
reminders, browser actions, and a FastAPI agent API.

## What It Does

- Runs a FastAPI Agent Protocol-like API.
- Connects a Telegram bot to the agent.
- Routes natural language requests to tools through an LLM router.
- Stores simple notes, tasks, reminders, and memory in local files.
- Can answer through OpenAI or local Ollama models.
- Supports research and page summarization tools.
- Supports browser actions and screenshots through a virtual display.
- Supports voice input through Whisper.
- Supports TTS replies through OpenAI speech.
- Supports image analysis through GPT-4o Vision.
- Includes a simple local dashboard.

## Architecture

```text
Telegram Bot
    |
    v
FastAPI Agent API (ap_agent.py)
    |
    v
Danny agent core (agent.py)
    |
    +--> tools/llm_openai.py
    +--> tools/memory.py
    +--> tools/reminders.py
    +--> tools/research.py
    +--> tools/browser.py
    +--> computer_skills.py
```

The API exposes a small Agent Protocol-like surface:

```text
POST /ap/v1/agent/tasks
POST /ap/v1/agent/tasks/{task_id}/steps
```

The Telegram bot sends user messages to this API. The agent then decides which
tool to use or falls back to an LLM answer.

## Key Files

```text
agent.py             Main agent logic and LLM routing
ap_agent.py          FastAPI API wrapper around the agent
telegram_bot.py      Telegram bot interface
reminder_bot.py      Reminder and calendar loop
dashboard.py         Simple local dashboard
computer_skills.py   Screenshot, mouse, keyboard, browser helpers
tools/               Agent tools
start_all.py         Local multi-process runner
```

## Tech Stack

- Python
- FastAPI
- Telegram Bot API
- OpenAI API
- Whisper / TTS / GPT-4o Vision
- Ollama for local model experiments
- Playwright / browser tooling
- WSL / Linux environment
- AutoGPT Forge foundation

## Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies. This prototype was originally based on AutoGPT Forge, so
the dependency set is larger than the custom MoyAgent code itself:

```bash
poetry install
```

Or install only the runtime dependencies you need manually for experiments.

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Required variables:

```text
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Never commit `.env`.

## Run API

```bash
source .venv/bin/activate
uvicorn ap_agent:app --host 0.0.0.0 --port 8011 --reload
```

## Run Telegram Bot

In another terminal:

```bash
source .venv/bin/activate
python telegram_bot.py
```

## Optional: Run All Local Components

`start_all.py` was used during local development to run the API, Telegram bot,
reminder loop, and virtual display together:

```bash
python start_all.py
```

This is a development helper, not a production process manager.

## Smoke Check

Compile the main files:

```bash
python -m py_compile agent.py ap_agent.py telegram_bot.py reminder_bot.py dashboard.py
```

Start the API and create a task/step through HTTP to verify the basic flow.

## Security Notes

This repository has been cleaned for public presentation:

- runtime files are ignored;
- `.env` is ignored;
- local databases are ignored;
- logs and generated output are ignored;
- Telegram token is read from `TELEGRAM_BOT_TOKEN`;
- OpenAI key is read from `OPENAI_API_KEY`.

If this repository was public before cleanup, rotate any tokens that were ever
committed in earlier history.

## Limitations

MoyAgent is a prototype:

- memory is file-based;
- tasks are simple local state;
- the API is minimal;
- the code mixes experiments and real agent logic;
- AutoGPT Forge code is still present;
- this is not intended for production deployment.

These limitations are exactly why the next step became Danny_Core.

## From MoyAgent To Danny_Core

MoyAgent helped me learn how AI agents work in practice: API orchestration,
Telegram integration, memory, tools, voice, vision, local models, and process
management.

After reaching the limits of a framework-based prototype, I started Danny_Core:
a cleaner custom platform with a FastAPI backend, Telegram bot, database-backed
memory, web frontend, auth, tests, deployment, and a more deliberate
architecture.

## Author

Alexey AI
