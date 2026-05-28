# Data Product: Artwork Engagement

## Назначение

Data Product `artwork_engagement` описывает вовлечённость посетителей онлайн-галереи:
просмотры, лайки, комментарии, активность виртуальных залов и агрегаты по выставкам.

## Владение

- Domain owner: команда продукта онлайн-галереи.
- Data owner: аналитик образовательной программы.
- Technical owner: data platform engineer.

## Интерфейсы

- Batch Raw: `s3://<bucket>/raw/gallery_engagement/artwork_submissions/`.
- Lakehouse Gold: `gallery.gold_artwork_engagement_daily`, `gallery.gold_artist_features`.
- Streaming input: Kafka topic `gallery.events`.
- Streaming aggregate: Kafka topic `gallery.occupancy_5m`.
- Serving: ClickHouse `gallery.gold_artwork_engagement_daily`, Cube API.

## SLA

- Batch ingestion: ежедневно до 06:00.
- Freshness Raw: не старше 24 часов.
- Real-time dashboard latency: до 2 минут после события.
- Availability semantic API: 99% для тестового стенда.

## Метрики качества

- `submission_id` уникален и не пустой.
- `artist_age` находится в диапазоне 6-17.
- `moderation_score` находится в диапазоне 0-100.
- Доля опубликованных работ рассчитывается только по валидным статусам.
- Для streaming-агрегатов обязательны `window_start`, `window_end`, `exhibition_id`, `room_id`.

## Потребители

- Embedded analytics в веб-интерфейсе галереи.
- Grafana real-time dashboard.
- ML-модель прогноза успешности публикации/вовлечённости работы.
