from __future__ import annotations

from datetime import UTC, datetime, timedelta
import sys
from pathlib import Path

from feast import FeatureStore


def main() -> None:
    repo_path = Path("feast/feature_repo")
    sys.path.insert(0, str(repo_path.resolve()))
    from features import artist, artist_artwork_features

    store = FeatureStore(repo_path=str(repo_path))
    end = datetime.now(UTC)
    start = end - timedelta(days=365)
    store.apply([artist, artist_artwork_features])
    store.materialize(start_date=start, end_date=end)


if __name__ == "__main__":
    main()
