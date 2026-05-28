# Publication Checklist

This checklist keeps MoyAgent safe and understandable as a public portfolio
repository.

## Current Public Status

- Runtime files are ignored by Git.
- `.env` is ignored by Git.
- Local databases are ignored by Git.
- Logs and generated output are ignored by Git.
- Telegram token is read from `TELEGRAM_BOT_TOKEN`.
- OpenAI key is read from `OPENAI_API_KEY`.
- README explains that this is a working prototype, not a production product.

## Before Pushing Public Updates

- Run `git status --short` and check that no local runtime files are staged.
- Run `python -m py_compile agent.py ap_agent.py telegram_bot.py reminder_bot.py dashboard.py`.
- Do not commit `.env`, local databases, logs, generated output, or personal
  notes.
- If any token was ever committed before cleanup, rotate it in the provider
  dashboard before relying on it again.

## What Is Acceptable To Keep

- Source code.
- Documentation.
- Example environment variables without real secrets.
- Small tutorials or architecture notes.
- Historical context that explains why the project exists.

## What Should Stay Local

- `.env`
- `agent.db`
- `DIARY.md`
- `memory.txt`
- `notes.txt`
- `tasks.txt`
- `reminders.txt`
- `output/`
- `logs/`
- any screenshots, exports, or notes containing personal data

## Suggested Repository Description

First AI-agent prototype built on AutoGPT / Forge: Telegram bot, FastAPI API,
memory, tools, voice, vision, reminders, and browser experiments. Historical
portfolio project that led to Danny_Core.

