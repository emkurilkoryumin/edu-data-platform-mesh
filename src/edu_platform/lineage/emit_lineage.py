from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def emit_lineage_event(
    job_name: str,
    inputs: list[str],
    outputs: list[str],
    metadata_dir: str | Path = "metadata/lineage/events",
    extra: dict[str, Any] | None = None,
) -> str:
    event = {
        "event_id": str(uuid4()),
        "event_time": datetime.now(UTC).isoformat(),
        "job_name": job_name,
        "inputs": inputs,
        "outputs": outputs,
        "extra": extra or {},
    }

    path = Path(metadata_dir)
    path.mkdir(parents=True, exist_ok=True)
    event_path = path / f"{event['event_time'].replace(':', '-')}_{event['event_id']}.json"
    event_path.write_text(json.dumps(event, indent=2), encoding="utf-8")
    return str(event_path)

