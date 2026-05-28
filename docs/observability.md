# Observability

## Airflow

- Retry включён в `gallery_raw_ingestion`: 3 попытки, exponential backoff.
- Failure callback отправляет сообщения в Slack и Telegram, если заданы переменные
  `SLACK_WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Логи задач доступны в Airflow UI.

## Data Quality

- Great Expectations suites находятся в `great_expectations/expectations`.
- CI сохраняет отчёт `metadata/quality/raw_quality_report.json`.
- При нарушении уникальности ключей или диапазонов DAG падает до записи некорректных данных в downstream.

## Lineage

- Статическая карта зависимостей: `metadata/lineage.yml`.
- Runtime events пишутся в `metadata/lineage/events/*.json`.

## Real-time Monitoring

- Flink агрегирует события в окна 5 минут с шагом 1 минута.
- ClickHouse хранит результаты в `gallery.gallery_occupancy_5m`.
- Grafana dashboard `Online Gallery Real-time Activity` показывает активных посетителей,
  просмотры и лайки по выставкам.
