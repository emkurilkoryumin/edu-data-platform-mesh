from edu_platform.etl.gallery_sources import build_artist_profiles, simulate_artwork_submissions
from edu_platform.quality.validate_raw import validate_dataframe


def test_raw_artwork_submissions_pass_quality_rules():
    df = simulate_artwork_submissions("2026-05-20")
    result = validate_dataframe(df, "raw_artwork_submissions")
    assert result.success


def test_duplicate_submission_id_fails_quality_rules():
    df = simulate_artwork_submissions("2026-05-20")
    df.loc[1, "submission_id"] = df.loc[0, "submission_id"]
    result = validate_dataframe(df, "raw_artwork_submissions")
    assert not result.success
    assert any("expect_column_values_to_be_unique" in item for item in result.failed_expectations)


def test_artist_profiles_pass_quality_rules():
    result = validate_dataframe(build_artist_profiles(), "raw_artist_profiles")
    assert result.success
