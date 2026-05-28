from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from edu_platform.etl.gallery_sources import build_artist_profiles, simulate_artwork_submissions
from edu_platform.quality.validate_raw import assert_valid


def main() -> None:
    output_dir = PROJECT_ROOT / "metadata" / "quality"
    output_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        assert_valid(simulate_artwork_submissions("2026-05-20"), "raw_artwork_submissions"),
        assert_valid(build_artist_profiles(), "raw_artist_profiles"),
    ]

    payload = {"success": all(check.success for check in checks), "checks": [check.as_dict() for check in checks]}
    (output_dir / "raw_quality_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if not payload["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
