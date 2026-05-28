#!/usr/bin/env python3
"""Smoke-check a running MoyAgent API instance.

This script intentionally uses only the Python standard library. It does not
import project modules, so it can verify the API from the outside.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8011"


def post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    try:
        task = post_json(
            "/ap/v1/agent/tasks",
            {"input": "Smoke test", "additional_input": {}},
        )
        task_id = task["task_id"]

        step = post_json(
            f"/ap/v1/agent/tasks/{task_id}/steps",
            {"input": "list_notes", "additional_input": {}},
        )
    except urllib.error.URLError as exc:
        print(f"FAIL: API is not reachable at {BASE_URL}: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: unexpected smoke-test error: {exc}")
        return 1

    if step.get("status") != "completed":
        print(f"FAIL: expected completed step, got: {step}")
        return 1

    print("OK: MoyAgent API created a task and completed a local step.")
    print(f"task_id={task_id}")
    print(f"output={step.get('output', '')[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

