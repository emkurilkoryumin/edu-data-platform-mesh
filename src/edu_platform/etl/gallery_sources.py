from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import random
import uuid

import pandas as pd


TECHNIQUES = ["watercolor", "gouache", "digital", "pencil", "acrylic", "mixed_media"]
CATEGORIES = ["portrait", "landscape", "abstract", "animals", "city", "fairy_tale"]
REGIONS = ["Moscow", "Saint Petersburg", "Kazan", "Novosibirsk", "Perm", "Sochi"]
MENTORS = ["School Studio", "Art Club", "Parent", "Museum Lab", "Online Course"]


def simulate_artwork_submissions(run_date: str, rows: int = 80, seed: int = 42) -> pd.DataFrame:
    """Simulate a paginated API response from the gallery website."""
    rng = random.Random(f"{run_date}-{seed}")
    base_dt = datetime.fromisoformat(run_date).replace(tzinfo=UTC)
    records: list[dict[str, object]] = []

    for idx in range(rows):
        artist_id = f"artist_{rng.randint(1, 40):04d}"
        artwork_id = f"art_{run_date.replace('-', '')}_{idx:04d}"
        moderation_score = round(rng.uniform(55, 100), 2)
        records.append(
            {
                "submission_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{run_date}-{idx}-{artist_id}")),
                "artist_id": artist_id,
                "artwork_id": artwork_id,
                "submitted_at": (base_dt + timedelta(minutes=idx * 7)).isoformat(),
                "title": f"Artwork {idx:04d}",
                "technique": rng.choice(TECHNIQUES),
                "category": rng.choice(CATEGORIES),
                "artist_age": rng.randint(6, 17),
                "moderation_score": moderation_score,
                "is_published": moderation_score >= 65,
                "source_system": "gallery_submissions_api",
            }
        )

    return pd.DataFrame.from_records(records)


def build_artist_profiles(rows: int = 40, seed: int = 7) -> pd.DataFrame:
    """Build a CSV-like export from the old gallery admin panel."""
    rng = random.Random(seed)
    records: list[dict[str, object]] = []
    for idx in range(1, rows + 1):
        age = rng.randint(6, 17)
        records.append(
            {
                "artist_id": f"artist_{idx:04d}",
                "display_name": f"Young Artist {idx:02d}",
                "age": age,
                "age_group": "6-9" if age <= 9 else "10-13" if age <= 13 else "14-17",
                "region": rng.choice(REGIONS),
                "mentor_type": rng.choice(MENTORS),
                "registered_at": (datetime(2025, 1, 1, tzinfo=UTC) + timedelta(days=idx)).isoformat(),
            }
        )

    return pd.DataFrame.from_records(records)


def write_artist_profiles_csv(path: str | Path) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    build_artist_profiles().to_csv(path, index=False)
    return str(path)


def read_artist_profiles_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)

