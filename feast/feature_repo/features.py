from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String


artist = Entity(
    name="artist",
    join_keys=["artist_id"],
    description="Young artist registered in the online gallery.",
)

artist_features_source = FileSource(
    name="artist_features_source",
    path="../../data/gold/artist_features.parquet",
    timestamp_field="event_timestamp",
)

artist_artwork_features = FeatureView(
    name="artist_artwork_features",
    entities=[artist],
    ttl=timedelta(days=365),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="age_group", dtype=String),
        Field(name="region", dtype=String),
        Field(name="mentor_type", dtype=String),
        Field(name="total_submissions", dtype=Int64),
        Field(name="published_submissions", dtype=Int64),
        Field(name="publication_rate", dtype=Float32),
        Field(name="avg_moderation_score", dtype=Float32),
        Field(name="unique_categories", dtype=Int64),
    ],
    online=True,
    source=artist_features_source,
    tags={"domain": "gallery_engagement", "layer": "gold"},
)
