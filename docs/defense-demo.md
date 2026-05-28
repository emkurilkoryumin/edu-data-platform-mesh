# Сценарий защиты

1. Показать Terraform:
   `terraform/` создаёт Object Storage, Managed Kafka, VM и cloud-init с Airflow Docker.

2. Показать домены:
   `docs/data-domains.md` и Data Product `docs/data-products/artwork_engagement.md`.

3. Запустить batch:
   Airflow DAG `gallery_raw_ingestion` генерирует данные старого сайта, проверяет качество и пишет Parquet в S3.

4. Показать качество:
   `great_expectations/expectations` содержит проверки уникальности ключей и диапазонов.

5. Показать lineage:
   `metadata/lineage.yml` и runtime JSON events показывают путь API/CSV → Raw → Lakehouse.

6. Показать Lakehouse:
   `src/edu_platform/lakehouse/spark_iceberg_job.py` создаёт Bronze/Silver/Gold Iceberg tables.

7. Показать Feature Store:
   `feast/feature_repo/features.py` регистрирует признаки художника для ML.

8. Показать streaming:
   `scripts/run_event_generator.sh` пишет события в Kafka, Flink SQL агрегирует окна.

9. Показать dashboard:
   Grafana читает ClickHouse real-time таблицу.

10. Показать embedded analytics:
    React UI получает метрики через Cube и делает drill-down выставка → возрастная группа.

11. Показать CI/CD:
    `.gitlab-ci.yml` запускает pytest, quality checks, build Docker images и deploy на stage.
