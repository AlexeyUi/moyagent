# Project Story

MoyAgent was my first practical AI-agent project.

It started as an experiment with AutoGPT / Forge and became the place where I
learned how an assistant is built from real moving parts: an API, a Telegram
interface, memory, tools, voice, vision, reminders, local files, and process
management.

This repository is not presented as a polished product. It is a historical
working prototype that shows the beginning of the path that later led to
Danny_Core.

## Timeline

- March 2026: first experiments with AutoGPT and agent frameworks.
- Late March 2026: MoyAgent prototype: Telegram bot, FastAPI API, tools,
  memory files, reminders, voice, and browser automation experiments.
- April 2026: the limitations of the framework-based approach became clear.
- April-May 2026: the ideas from MoyAgent were rebuilt as Danny_Core, a custom
  multi-user assistant platform with a cleaner architecture.

## What I Learned

MoyAgent helped me understand several practical parts of AI-agent development:

- how a Telegram bot can talk to a backend API;
- how an LLM can route requests to tools;
- where simple file-based memory works and where it breaks down;
- why production assistants need clear ownership, database-backed state, tests,
  configuration discipline, and deployment rules;
- why prototypes are useful, but eventually need to be replaced by a deliberate
  architecture.

## Why This Repository Still Exists

MoyAgent is kept public because it shows the learning process.

It is useful as a portfolio artifact because it demonstrates:

- early hands-on work with agent architecture;
- integration of multiple AI capabilities;
- the transition from framework experimentation to a custom system;
- the ability to clean up and document an old prototype instead of hiding it.

The production-focused continuation of this work is Danny_Core:

https://github.com/AlexeyUi/Danny_Core

