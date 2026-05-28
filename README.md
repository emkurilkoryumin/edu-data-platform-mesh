# Edu Gallery Data Platform Mesh

Учебный проект для задания по доменно-ориентированной data platform на базе кейса
старого сайта: онлайн-галерея юных художников.

## Что покрыто

- Часть 1: Terraform для Yandex Cloud: Object Storage, Managed Kafka, VM с Docker/Airflow.
- Часть 2: Airflow DAG для загрузки симулированного API галереи и CSV-выгрузок в Raw/Bronze S3 Parquet, Great Expectations, retry, Slack/Telegram alerts, lineage.
- Часть 3: Spark + Apache Iceberg lakehouse слои Bronze/Silver/Gold и Feast Feature Store.
- Часть 4: Kafka event generator, Flink SQL aggregation, ClickHouse sink, Grafana dashboard.
- Часть 5: Cube semantic layer и React embedded analytics с drill-down.
- Часть 6: GitLab CI/CD, pytest, data quality checks, Docker build, deploy over SSH, ADR и документация для защиты.

## Домены данных

- `artwork_catalog`: работы, техники, категории, статусы модерации.
- `young_artist_profile`: юные художники, возрастные группы, регионы, наставники.
- `gallery_engagement`: просмотры, лайки, избранное, комментарии, посещения выставок.
- `submission_moderation`: загрузки работ, проверки безопасности, SLA публикации.
- `virtual_exhibition_infrastructure`: виртуальные залы, экспозиции, доступность и нагрузка.

## Происхождение данных

В проекте используются воспроизводимые синтетические данные учебного стенда, а не реальные
персональные данные юных художников. Источник, правила генерации, lineage и проверки
качества описаны в `docs/data-provenance.md`.

## Быстрый локальный запуск

```bash
cp .env.example .env
docker compose up -d --build minio kafka clickhouse grafana cube webapp
docker compose up -d --build airflow-init airflow-webserver airflow-scheduler
```

Airflow: http://localhost:8080, логин `admin`, пароль `admin`.
Grafana: http://localhost:3000, логин `admin`, пароль `admin`.
Cube API: http://localhost:4000/cubejs-api/v1.
React UI: http://localhost:5173.

## Cloud deploy

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Секреты и реальные cloud credentials не хранятся в репозитории.

## Проверки

```bash
python -m compileall src tests airflow/dags
pytest
great_expectations checkpoint run gallery_raw_checkpoint
```

Если зависимости не установлены локально, запускайте проверки внутри Docker/Airflow image.

## Проверенный локальный запуск вне VM

На текущей машине сервисы проверены через Docker Compose и доступны по адресам:

- React/demo UI: http://localhost:5173
- Airflow: http://localhost:8080, логин `admin`, пароль `admin`
- Grafana: http://localhost:3000, логин `admin`, пароль `admin`
- Cube API: http://localhost:4000
- MinIO Console: http://localhost:9001, логин `gallery`, пароль `gallery-secret`
- ClickHouse HTTP: http://localhost:8123

Для повторного запуска:

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
docker compose up -d
```

Если контейнеры пересоздаются с нуля, сначала выполните:

```bash
cp -n .env.example .env
docker compose up -d --build
```
