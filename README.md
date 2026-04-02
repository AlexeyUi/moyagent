# MoyAgent

MoyAgent is a personal AI agent project focused on automation, research, browser tasks, and assistant workflows.

## Overview

MoyAgent is built as a practical AI assistant that can perform useful actions, work with tools, collect information, and support real automation scenarios. The goal is a modular, expandable agent that can be adapted for freelance tasks and product solutions.

## Features

- Browser-based task automation
- Research and information summarization
- LLM-based assistant workflows
- Modular tool structure
- SQLite memory and state tracking
- Docker support
- Expandable for future integrations

## Tech stack

- Python 3.12
- FastAPI
- Playwright
- Ollama (local LLM)
- SQLite
- Docker
- Git / Linux / WSL

## Project structure

```
moyagent/
├── agent.py              # Main agent entry point
├── ap_agent.py
├── computer_skills.py
├── dashboard.py
├── tools/                # Tool modules
├── docs/                 # Documentation
├── tests/                # Tests
├── tutorials/            # Usage examples
├── forge/                # Agent framework
├── output/               # Agent output
├── .env.example          # Environment config template
├── Dockerfile
└── README.md
```

## Getting started

```bash
# Clone the repository
git clone https://github.com/AlexeyUi/moyagent.git
cd moyagent

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings

# Run the agent
python agent.py
```

## Why I built it

MoyAgent is my foundation for practical AI automation. I am building it as a base for freelance solutions, real task automation, and my own product ecosystem.

## Roadmap

- [ ] Improve tool reliability
- [ ] Add more task workflows
- [ ] Expand memory and context management
- [ ] Connect Telegram interface
- [ ] Production deployment on VPS

## Status

Active development.

## Author

[Alexey AI](https://github.com/AlexeyUi)
