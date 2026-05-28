# Инструкция по развертыванию

## Локально

```bash
cp .env.example .env
docker compose up -d --build minio create-buckets kafka clickhouse grafana cube webapp
docker compose up -d --build airflow-init airflow-webserver airflow-scheduler
```

Запуск batch DAG:

```bash
docker compose exec airflow-scheduler airflow dags trigger gallery_raw_ingestion
```

Запуск генератора событий:

```bash
KAFKA_PUBLIC_BOOTSTRAP_SERVERS=localhost:9092 ./scripts/run_event_generator.sh
```

Запуск Flink SQL:

```bash
docker compose up -d --build flink-jobmanager flink-taskmanager
./scripts/submit_flink_sql.sh
```

## Yandex Cloud

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

После apply Terraform выводит `airflow_url`, `grafana_url`, `bucket_name`,
`kafka_cluster_id`.

## GitLab CI/CD

Нужные CI variables:

- `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` стандартно выдаются GitLab.
- `STAGE_HOST` - IP тестового стенда.
- `STAGE_USER` - обычно `ubuntu`.
- `STAGE_SSH_PRIVATE_KEY` - приватный ключ для deploy.

Pipeline выполняет compile, pytest, quality checks, Docker build и manual deploy.

## Проверенный локальный стенд

Для запуска вне облачной VM используйте текущий Docker Compose:

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
cp -n .env.example .env
docker compose up -d --build
```

После запуска откройте:

- `http://localhost:5173` - локальная embedded analytics витрина.
- `http://localhost:8080` - Airflow, `admin/admin`.
- `http://localhost:3000` - Grafana, `admin/admin`.
- `http://localhost:4000` - Cube API.
- `http://localhost:9001` - MinIO Console, `gallery/gallery-secret`.

ClickHouse-плагин Grafana сохранён в `grafana/plugins`, поэтому Grafana не должна скачивать его при каждом старте.
