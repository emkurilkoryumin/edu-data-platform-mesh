from __future__ import annotations

import pandas as pd


def build_artist_features(submissions: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    """Build a Gold feature table for ML models predicting artwork success."""
    submissions = submissions.copy()
    submissions["submitted_at"] = pd.to_datetime(submissions["submitted_at"], utc=True)

    grouped = (
        submissions.groupby("artist_id")
        .agg(
            total_submissions=("submission_id", "count"),
            published_submissions=("is_published", "sum"),
            avg_moderation_score=("moderation_score", "mean"),
            unique_categories=("category", "nunique"),
            last_submission_at=("submitted_at", "max"),
        )
        .reset_index()
    )
    grouped["publication_rate"] = grouped["published_submissions"] / grouped["total_submissions"]

    features = grouped.merge(profiles, on="artist_id", how="left")
    features["event_timestamp"] = features["last_submission_at"]
    return features[
        [
            "artist_id",
            "event_timestamp",
            "age",
            "age_group",
            "region",
            "mentor_type",
            "total_submissions",
            "published_submissions",
            "publication_rate",
            "avg_moderation_score",
            "unique_categories",
        ]
    ]


def build_daily_artwork_engagement(submissions: pd.DataFrame) -> pd.DataFrame:
    submissions = submissions.copy()
    submissions["submitted_at"] = pd.to_datetime(submissions["submitted_at"], utc=True)
    submissions["event_date"] = submissions["submitted_at"].dt.date.astype(str)
    return (
        submissions.groupby(["event_date", "category", "technique"])
        .agg(
            submissions_count=("submission_id", "count"),
            published_count=("is_published", "sum"),
            avg_moderation_score=("moderation_score", "mean"),
            active_artists=("artist_id", "nunique"),
        )
        .reset_index()
    )

