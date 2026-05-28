CREATE DATABASE IF NOT EXISTS gallery;

CREATE TABLE IF NOT EXISTS gallery.gallery_occupancy_5m
(
    window_start DateTime,
    window_end DateTime,
    exhibition_id LowCardinality(String),
    room_id LowCardinality(String),
    active_visitors UInt64,
    views UInt64,
    likes UInt64,
    submissions_started UInt64,
    inserted_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (window_start, exhibition_id, room_id);

CREATE TABLE IF NOT EXISTS gallery.gallery_occupancy_5m_queue
(
    window_start String,
    window_end String,
    exhibition_id String,
    room_id String,
    active_visitors UInt64,
    views UInt64,
    likes UInt64,
    submissions_started UInt64
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'gallery.occupancy_5m',
    kafka_group_name = 'clickhouse-gallery-occupancy',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;

CREATE MATERIALIZED VIEW IF NOT EXISTS gallery.gallery_occupancy_5m_mv
TO gallery.gallery_occupancy_5m
AS
SELECT
    parseDateTimeBestEffort(window_start) AS window_start,
    parseDateTimeBestEffort(window_end) AS window_end,
    exhibition_id,
    room_id,
    active_visitors,
    views,
    likes,
    submissions_started
FROM gallery.gallery_occupancy_5m_queue;

CREATE TABLE IF NOT EXISTS gallery.gold_artwork_engagement_daily
(
    event_date Date,
    exhibition_id LowCardinality(String),
    category LowCardinality(String),
    age_group LowCardinality(String),
    student_count UInt64,
    artwork_count UInt64,
    avg_moderation_score Float64,
    views UInt64,
    likes UInt64
)
ENGINE = MergeTree
ORDER BY (event_date, exhibition_id, category, age_group);

INSERT INTO gallery.gold_artwork_engagement_daily
SELECT *
FROM
(
    SELECT
        toDate('2026-05-18') AS event_date,
        'spring_colors' AS exhibition_id,
        'landscape' AS category,
        '10-13' AS age_group,
        24 AS student_count,
        41 AS artwork_count,
        83.4 AS avg_moderation_score,
        1200 AS views,
        215 AS likes
    UNION ALL
    SELECT toDate('2026-05-18'), 'digital_future', 'digital', '14-17', 18, 35, 88.2, 980, 190
    UNION ALL
    SELECT toDate('2026-05-19'), 'animals_and_friends', 'animals', '6-9', 31, 52, 79.5, 1470, 266
) seed
WHERE NOT EXISTS (SELECT 1 FROM gallery.gold_artwork_engagement_daily LIMIT 1);

INSERT INTO gallery.gallery_occupancy_5m
SELECT
    now() - toIntervalMinute(number) AS window_start,
    now() - toIntervalMinute(number) + toIntervalMinute(5) AS window_end,
    multiIf(number % 3 = 0, spring_colors, number % 3 = 1, digital_future, animals_and_friends) AS exhibition_id,
    multiIf(number % 4 = 0, main_hall, number % 4 = 1, watercolor_room, number % 4 = 2, digital_room, mentor_choice) AS room_id,
    18 + (number % 23) AS active_visitors,
    90 + number * 7 AS views,
    8 + (number % 17) AS likes,
    number % 5 AS submissions_started
FROM numbers(60)
WHERE NOT EXISTS (SELECT 1 FROM gallery.gallery_occupancy_5m LIMIT 1);
