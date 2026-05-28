CREATE TABLE gallery_events (
  event_id STRING,
  event_ts BIGINT,
  event_type STRING,
  visitor_id STRING,
  artist_id STRING,
  artwork_id STRING,
  exhibition_id STRING,
  room_id STRING,
  session_id STRING,
  source_system STRING,
  event_time AS TO_TIMESTAMP_LTZ(event_ts, 3),
  WATERMARK FOR event_time AS event_time - INTERVAL '10' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'gallery.events',
  'properties.bootstrap.servers' = 'kafka:29092',
  'properties.group.id' = 'flink-gallery-window-aggregation',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json',
  'json.ignore-parse-errors' = 'true'
);

CREATE TABLE gallery_occupancy_5m (
  window_start STRING,
  window_end STRING,
  exhibition_id STRING,
  room_id STRING,
  active_visitors BIGINT,
  views BIGINT,
  likes BIGINT,
  submissions_started BIGINT
) WITH (
  'connector' = 'kafka',
  'topic' = 'gallery.occupancy_5m',
  'properties.bootstrap.servers' = 'kafka:29092',
  'format' = 'json'
);

INSERT INTO gallery_occupancy_5m
SELECT
  DATE_FORMAT(HOP_START(event_time, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE), 'yyyy-MM-dd HH:mm:ss') AS window_start,
  DATE_FORMAT(HOP_END(event_time, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE), 'yyyy-MM-dd HH:mm:ss') AS window_end,
  exhibition_id,
  room_id,
  COUNT(DISTINCT visitor_id) AS active_visitors,
  SUM(CASE WHEN event_type = 'artwork_viewed' THEN 1 ELSE 0 END) AS views,
  SUM(CASE WHEN event_type = 'artwork_liked' THEN 1 ELSE 0 END) AS likes,
  SUM(CASE WHEN event_type = 'submission_started' THEN 1 ELSE 0 END) AS submissions_started
FROM gallery_events
GROUP BY
  HOP(event_time, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE),
  exhibition_id,
  room_id;
