from edu_platform.etl.gallery_sources import build_artist_profiles, simulate_artwork_submissions
from edu_platform.lakehouse.transforms import build_artist_features, build_daily_artwork_engagement


def test_build_artist_features_has_expected_columns():
    submissions = simulate_artwork_submissions("2026-05-20", rows=20)
    profiles = build_artist_profiles(rows=40)

    features = build_artist_features(submissions, profiles)

    assert "artist_id" in features.columns
    assert "publication_rate" in features.columns
    assert features["publication_rate"].between(0, 1).all()


def test_build_daily_artwork_engagement_aggregates_rows():
    submissions = simulate_artwork_submissions("2026-05-20", rows=20)

    gold = build_daily_artwork_engagement(submissions)

    assert gold["submissions_count"].sum() == 20
    assert {"event_date", "category", "technique"}.issubset(gold.columns)
