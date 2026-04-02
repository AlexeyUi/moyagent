from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime

from agent import Danny

app = FastAPI()

moy_agent = Danny()  # один экземпляр агента

class Message(BaseModel):
    role: str
    content: str

class TaskCreateRequest(BaseModel):
    input: str
    additional_input: Dict[str, Any] = {}

class StepCreateRequest(BaseModel):
    input: str
    additional_input: Dict[str, Any] = {}

# очень простое хранилище задач в памяти
TASKS: Dict[str, Dict[str, Any]] = {}

@app.post("/ap/v1/agent/tasks")
async def create_task(body: TaskCreateRequest):
    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    TASKS[task_id] = {
        "input": body.input,
        "additional_input": body.additional_input,
        "created_at": now,
        "modified_at": now,
        "artifacts": [],
        "history": [],
    }
    return {
        "input": body.input,
        "additional_input": body.additional_input,
        "created_at": now,
        "modified_at": now,
        "task_id": task_id,
        "artifacts": [],
    }

@app.post("/ap/v1/agent/tasks/{task_id}/steps")
async def create_step(task_id: str, body: StepCreateRequest):
    if task_id not in TASKS:
        return {"detail": "Task not found"}

    history: List[Dict[str, str]] = TASKS[task_id]["history"]

    # вызываем Danny без forge.sdk
    step_request = type("StepReq", (), {})()
    step_request.task_id = task_id
    step_request.input = body.input
    step_request.additional_input = body.additional_input or {}

    step = await moy_agent.execute_step(step_request)
    answer = getattr(step, "output", "") or ""

    # сохраняем в историю
    history.append({"role": "user", "content": body.input})
    history.append({"role": "assistant", "content": answer})
    TASKS[task_id]["modified_at"] = datetime.utcnow().isoformat()

    step_id = str(uuid.uuid4())
    return {
        "name": body.input,
        "input": body.input,
        "additional_input": body.additional_input,
        "created_at": TASKS[task_id]["created_at"],
        "modified_at": TASKS[task_id]["modified_at"],
        "task_id": task_id,
        "step_id": step_id,
        "status": "completed",
        "output": answer,
        "additional_output": None,
        "artifacts": [],
        "is_last": False,
    }

