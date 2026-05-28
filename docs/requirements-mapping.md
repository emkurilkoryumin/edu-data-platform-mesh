# Карта требований задания

## Часть 1

- Домены данных: `docs/data-domains.md`.
- Terraform Object Storage, Managed Kafka, VM: `terraform/main.tf`.
- Airflow in Docker on VM: `terraform/templates/cloud-init.yaml.tftpl`.
- Data Product: `docs/data-products/artwork_engagement.md`, `docs/data-products/artwork_engagement_product.yaml`.

## Часть 2

- Airflow DAG загрузки API + CSV в S3 Parquet: `airflow/dags/gallery_raw_ingestion_dag.py`.
- Источники и S3 writer: `src/edu_platform/etl/`.
- Great Expectations suites: `great_expectations/expectations/`.
- Retry и Slack/Telegram alerts: `airflow/dags/gallery_raw_ingestion_dag.py`, `src/edu_platform/utils/alerts.py`.
- Lineage: `metadata/lineage.yml`, `src/edu_platform/lineage/emit_lineage.py`.

## Часть 3

- Bronze/Silver/Gold Iceberg job: `src/edu_platform/lakehouse/spark_iceberg_job.py`.
- Gold transformations: `src/edu_platform/lakehouse/transforms.py`.
- Feature table: `metadata/lakehouse/gallery_gold.sql`.
- Feast Feature Store: `feast/feature_repo/`.

## Часть 4

- Kafka event generator: `src/edu_platform/streaming/gallery_event_generator.py`.
- Flink window aggregation: `flink/sql/gallery_window_aggregation.sql`.
- ClickHouse sink: `clickhouse/init/001_gallery_schema.sql`.
- Grafana dashboard: `grafana/dashboards/gallery_realtime.json`.

## Часть 5

- Cube semantic layer: `cube/schema/`.
- React embedded analytics: `webapp/src/`.
- Drill-down: `webapp/src/App.jsx`.

## Часть 6

- GitLab CI/CD: `.gitlab-ci.yml`.
- pytest: `tests/`.
- Data quality CI script: `scripts/run_quality_checks.py`.
- Deploy script: `scripts/deploy_staging.sh`.
- ADR and docs: `docs/adr/`, `docs/deployment.md`, `docs/defense-demo.md`.
