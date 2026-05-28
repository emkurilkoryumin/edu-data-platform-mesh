from __future__ import annotations

import os
from typing import Any

import requests


def notify_failure(context: dict[str, Any]) -> None:
    """Send Airflow failure notifications to Slack and/or Telegram if configured."""
    dag_id = context.get("dag").dag_id if context.get("dag") else "unknown_dag"
    task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown_task"
    run_id = context.get("run_id", "unknown_run")
    exception = context.get("exception", "no exception in context")
    message = f"Gallery data pipeline failed: dag={dag_id}, task={task_id}, run={run_id}, error={exception}"

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_webhook_url:
        requests.post(slack_webhook_url, json={"text": message}, timeout=10).raise_for_status()

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_bot_token and telegram_chat_id:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        requests.post(url, json={"chat_id": telegram_chat_id, "text": message}, timeout=10).raise_for_status()

