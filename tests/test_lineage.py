import json
from pathlib import Path

from edu_platform.lineage.emit_lineage import emit_lineage_event


def test_emit_lineage_event_writes_json(tmp_path):
    event_path = emit_lineage_event(
        job_name="test_job",
        inputs=["api://source"],
        outputs=["s3://bucket/raw/data.parquet"],
        metadata_dir=tmp_path,
        extra={"domain": "gallery_engagement"},
    )

    payload = json.loads((tmp_path / Path(event_path).name).read_text(encoding="utf-8"))
    assert payload["job_name"] == "test_job"
    assert payload["inputs"] == ["api://source"]
    assert payload["outputs"] == ["s3://bucket/raw/data.parquet"]
    assert payload["extra"]["domain"] == "gallery_engagement"
