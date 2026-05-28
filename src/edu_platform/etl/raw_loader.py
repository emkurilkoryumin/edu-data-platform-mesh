from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from edu_platform.config import PlatformConfig
from edu_platform.etl.gallery_sources import (
    read_artist_profiles_csv,
    simulate_artwork_submissions,
    write_artist_profiles_csv,
)
from edu_platform.etl.s3_io import put_dataframe_as_parquet
from edu_platform.lineage.emit_lineage import emit_lineage_event
from edu_platform.quality.validate_raw import assert_valid


def normalize_run_date(run_date: str | None = None) -> str:
    if run_date:
        return run_date[:10]
    return datetime.now(UTC).date().isoformat()


def load_artwork_submissions_raw(run_date: str | None = None) -> dict[str, str]:
    config = PlatformConfig.from_env()
    date = normalize_run_date(run_date)
    df = simulate_artwork_submissions(date)
    assert_valid(df, "raw_artwork_submissions")

    key = f"raw/gallery_engagement/artwork_submissions/ingestion_date={date}/{uuid4()}.parquet"
    uri = put_dataframe_as_parquet(df, config.s3_bucket, key, config)
    lineage_path = emit_lineage_event(
        job_name="load_artwork_submissions_raw",
        inputs=["api://old-gallery/submissions"],
        outputs=[uri],
        extra={"domain": "gallery_engagement", "dataset": "artwork_submissions"},
    )
    return {"dataset": "raw_artwork_submissions", "s3_uri": uri, "lineage_path": lineage_path}


def load_artist_profiles_raw(run_date: str | None = None, staging_dir: str = "/tmp/edu_gallery_sources") -> dict[str, str]:
    config = PlatformConfig.from_env()
    date = normalize_run_date(run_date)
    csv_path = write_artist_profiles_csv(Path(staging_dir) / f"artist_profiles_{date}.csv")
    df = read_artist_profiles_csv(csv_path)
    assert_valid(df, "raw_artist_profiles")

    key = f"raw/young_artist_profile/artist_profiles/ingestion_date={date}/{uuid4()}.parquet"
    uri = put_dataframe_as_parquet(df, config.s3_bucket, key, config)
    lineage_path = emit_lineage_event(
        job_name="load_artist_profiles_raw",
        inputs=[f"file://{csv_path}"],
        outputs=[uri],
        extra={"domain": "young_artist_profile", "dataset": "artist_profiles"},
    )
    return {"dataset": "raw_artist_profiles", "s3_uri": uri, "lineage_path": lineage_path}

