CREATE TABLE IF NOT EXISTS gallery.gold_artwork_engagement_daily (
  event_date DATE,
  category STRING,
  technique STRING,
  submissions_count BIGINT,
  published_count BIGINT,
  avg_moderation_score DOUBLE,
  active_artists BIGINT
) USING iceberg;

CREATE TABLE IF NOT EXISTS gallery.gold_artist_features (
  artist_id STRING,
  event_timestamp TIMESTAMP,
  age INT,
  age_group STRING,
  region STRING,
  mentor_type STRING,
  total_submissions BIGINT,
  published_submissions BIGINT,
  publication_rate DOUBLE,
  avg_moderation_score DOUBLE,
  unique_categories BIGINT
) USING iceberg;
