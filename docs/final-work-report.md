# Итоговый отчёт по выполненной работе

Проект: `edu-data-platform-mesh`

Кейс: старый сайт был онлайн-галереей юных художников.

Дата итоговой проверки: 22 мая 2026.

## 1. Цель работы

Целью работы было спроектировать и реализовать основу современной data platform для онлайн-галереи юных художников. Платформа должна покрывать доменно-ориентированную архитектуру, облачную инфраструктуру как код, batch ETL/ELT, контроль качества данных, lakehouse, feature store, streaming, real-time dashboard, semantic layer, embedded analytics и CI/CD.

Проект сделан не как набор отдельных примеров, а как связанный учебный стенд вокруг одного бизнес-кейса: сайт принимает работы юных художников, хранит профили авторов, показывает виртуальные выставки и собирает события вовлечённости посетителей.

## 2. Общая архитектура

Архитектура построена вокруг следующих компонентов:

- Yandex Cloud Terraform infrastructure для облачного развёртывания.
- S3-compatible Object Storage как Data Lake.
- Managed Kafka для событий сайта.
- VM с Docker Compose для Airflow и вспомогательных сервисов.
- Airflow для batch orchestration.
- Great Expectations для проверок качества Raw-данных.
- Apache Spark + Apache Iceberg для Lakehouse слоёв Bronze, Silver и Gold.
- Feast как Feature Store.
- Kafka + Flink + ClickHouse для real-time обработки.
- Grafana для real-time dashboard.
- Cube.js для semantic layer.
- Web UI для embedded analytics и drill-down.
- GitLab CI/CD для автоматизации тестов, проверок, сборки и деплоя.

Схема архитектуры описана в файле:

`docs/architecture.md`

## 3. Часть 1. Доменно-ориентированная архитектура и Infrastructure as Code

### 3.1. Определённые домены данных

Для кейса онлайн-галереи выделены домены:

- `artwork_catalog` - каталог художественных работ, техники, категории, статусы публикации.
- `young_artist_profile` - профили юных художников, возрастные группы, регионы, наставники.
- `gallery_engagement` - просмотры, лайки, комментарии, действия посетителей.
- `submission_moderation` - загрузка и модерация работ.
- `virtual_exhibition_infrastructure` - виртуальные залы, активность, доступность, нагрузка.

Описание доменов находится в:

`docs/data-domains.md`

### 3.2. Terraform

Созданы Terraform-конфигурации для Yandex Cloud:

- VPC network.
- Subnet.
- Security group.
- S3-compatible Object Storage bucket.
- Service account и static access key для S3.
- Managed Kafka cluster.
- Kafka topics `gallery.events` и `gallery.occupancy_5m`.
- Kafka application user.
- Compute VM для Docker orchestration.
- Cloud-init bootstrap для установки Docker и запуска Airflow.

Основные файлы:

- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`
- `terraform/versions.tf`
- `terraform/templates/cloud-init.yaml.tftpl`
- `terraform/terraform.tfvars.example`

### 3.3. Airflow на VM

В cloud-init описан запуск Airflow в Docker Compose на созданной VM. Для локального режима Airflow также описан в основном `docker-compose.yml`.

## 4. Часть 2. Отказоустойчивые ETL/ELT pipeline с Observability

### 4.1. Airflow DAG

Создан DAG:

`airflow/dags/gallery_raw_ingestion_dag.py`

DAG выполняет загрузку данных из двух типов источников:

- симулированный API старого сайта галереи с данными о загруженных работах;
- CSV-выгрузка профилей юных художников из административной панели.

Данные сохраняются в S3-compatible storage в формате Parquet.

### 4.2. Источники данных и запись в S3

Реализованы Python-модули:

- `src/edu_platform/etl/gallery_sources.py`
- `src/edu_platform/etl/raw_loader.py`
- `src/edu_platform/etl/s3_io.py`

Они генерируют реалистичные данные для кейса галереи, валидируют их и записывают в Raw-слой.

### 4.3. Great Expectations

Добавлены expectation suites:

- `great_expectations/expectations/raw_artwork_submissions.json`
- `great_expectations/expectations/raw_artist_profiles.json`

Проверяются:

- отсутствие пустых ключей;
- уникальность `submission_id`;
- уникальность `artist_id`;
- диапазон возраста художника от 6 до 17;
- диапазон `moderation_score` от 0 до 100;
- допустимые значения техник и возрастных групп.

### 4.4. Retry и алерты

В Airflow DAG настроены:

- `retries = 3`;
- `retry_delay`;
- `retry_exponential_backoff`;
- `max_retry_delay`;
- callback на падение задачи.

Оповещения реализованы в:

`src/edu_platform/utils/alerts.py`

Поддерживаются Telegram и Slack через переменные окружения.

### 4.5. Data Lineage

Lineage реализован двумя способами:

- статическая карта зависимостей: `metadata/lineage.yml`;
- runtime lineage events: `src/edu_platform/lineage/emit_lineage.py`.

## 5. Часть 3. Lakehouse и Feature Store

### 5.1. Bronze, Silver, Gold

Создан Spark job:

`src/edu_platform/lakehouse/spark_iceberg_job.py`

Он описывает Lakehouse на Apache Iceberg поверх S3:

- Bronze: сырые данные из Raw.
- Silver: очищенные и дедуплицированные данные.
- Gold: агрегаты и таблица признаков.

### 5.2. Gold transformations

Трансформации вынесены в:

`src/edu_platform/lakehouse/transforms.py`

Реализованы:

- ежедневные агрегаты по выставкам, категориям и техникам;
- признаки художника для ML-модели.

### 5.3. Таблица признаков

Gold feature table содержит:

- `artist_id`;
- `age`;
- `age_group`;
- `region`;
- `mentor_type`;
- `total_submissions`;
- `published_submissions`;
- `publication_rate`;
- `avg_moderation_score`;
- `unique_categories`.

SQL-схема описана в:

`metadata/lakehouse/gallery_gold.sql`

### 5.4. Feast Feature Store

Feast настроен в:

- `feast/feature_repo/feature_store.yaml`
- `feast/feature_repo/features.py`
- `scripts/materialize_features.py`

Зарегистрирована entity `artist` и feature view `artist_artwork_features`.

## 6. Часть 4. Streaming pipeline и real-time dashboard

### 6.1. Kafka event generator

Создан генератор событий сайта:

`src/edu_platform/streaming/gallery_event_generator.py`

Он генерирует события:

- `artwork_viewed`;
- `artwork_liked`;
- `comment_added`;
- `submission_started`;
- `virtual_room_entered`.

События пишутся в Kafka topic:

`gallery.events`

### 6.2. Flink SQL aggregation

Flink SQL job находится в:

`flink/sql/gallery_window_aggregation.sql`

Он агрегирует события в hopping window:

- размер окна: 5 минут;
- шаг: 1 минута.

Результат пишется в Kafka topic:

`gallery.occupancy_5m`

### 6.3. ClickHouse

ClickHouse схема создана в:

`clickhouse/init/001_gallery_schema.sql`

Созданы таблицы:

- `gallery.gallery_occupancy_5m`;
- `gallery.gallery_occupancy_5m_queue`;
- `gallery.gallery_occupancy_5m_mv`;
- `gallery.gold_artwork_engagement_daily`.

### 6.4. Grafana

Grafana dashboard:

`grafana/dashboards/gallery_realtime.json`

Datasource:

`grafana/provisioning/datasources/clickhouse.yml`

ClickHouse plugin сохранён локально:

`grafana/plugins/grafana-clickhouse-datasource`

Это нужно, чтобы Grafana не пыталась скачивать plugin при каждом запуске.

## 7. Часть 5. Semantic Layer и Embedded Analytics

### 7.1. Cube.js

Cube semantic layer описан в:

- `cube/schema/ArtworkEngagement.js`
- `cube/schema/RoomUtilization.js`
- `cube/model/ArtworkEngagement.js`
- `cube/model/RoomUtilization.js`

Cube описывает бизнес-метрики:

- `StudentCount`;
- `ArtworkCount`;
- `Views`;
- `Likes`;
- `AvgGrade`;
- `RoomUtilization`.

### 7.2. Embedded UI

Реализован веб-интерфейс:

- React-исходники: `webapp/src`;
- локальная демо-витрина без npm install: `webapp/static`;
- Node server: `webapp/server.js`.

Локальный UI доступен по адресу:

`http://localhost:5173`

В интерфейсе реализован drill-down:

выставка -> возрастные группы художников.

## 8. Часть 6. CI/CD и документация

### 8.1. GitLab CI/CD

Pipeline описан в:

`.gitlab-ci.yml`

Он включает стадии:

- `validate`;
- `test`;
- `data_quality`;
- `build`;
- `deploy`.

Pipeline выполняет:

- компиляцию Python-кода;
- pytest;
- проверки качества данных;
- сборку Docker images;
- deploy на staging по SSH.

### 8.2. Тесты

Добавлены тесты:

- `tests/test_quality_rules.py`
- `tests/test_lakehouse_transforms.py`

Тесты проверяют:

- прохождение quality rules;
- падение на дубликатах ключей;
- корректность feature transformations;
- корректность daily aggregations.

### 8.3. Документация

Подготовлены документы:

- `docs/architecture.md`
- `docs/data-domains.md`
- `docs/data-products/artwork_engagement.md`
- `docs/data-products/artwork_engagement_product.yaml`
- `docs/adr/0001-domain-oriented-gallery-platform.md`
- `docs/deployment.md`
- `docs/observability.md`
- `docs/defense-demo.md`
- `docs/requirements-mapping.md`
- `docs/local-run-report.md`

## 9. Проверенный локальный запуск

Проект проверен локально вне VM через Docker Compose.

### 9.1. Команда запуска

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
docker compose up -d webapp
```

Для полного стека:

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
docker compose up -d minio kafka clickhouse cube grafana airflow-webserver airflow-scheduler webapp
```

Не рекомендуется запускать просто `docker compose up -d` на слабом окружении, потому что он может начать собирать тяжёлый Flink image.

### 9.2. Проверенные URL

- Главный локальный сайт: `http://localhost:5173`
- Airflow: `http://localhost:8080`
- Grafana: `http://localhost:3000`
- Cube API: `http://localhost:4000`
- MinIO Console: `http://localhost:9001`
- ClickHouse HTTP: `http://localhost:8123`

### 9.3. Логины

Airflow:

- login: `admin`
- password: `admin`

Grafana:

- login: `admin`
- password: `admin`

MinIO:

- login: `gallery`
- password: `gallery-secret`

## 10. Фактические проверки

Выполнены проверки:

- `docker compose config --quiet` - успешно.
- `python3 -m compileall src tests airflow/dags scripts` - успешно.
- `node --check webapp/server.js` - успешно.
- `curl http://localhost:5173` - `HTTP 200 OK`.
- `curl http://localhost:3000` - Grafana отвечает.
- `curl http://localhost:4000` - Cube отвечает.
- `curl http://localhost:9001` - MinIO отвечает.
- `curl http://localhost:8123/?query=SELECT%201` - ClickHouse вернул `1`.
- Cube API вернул данные из ClickHouse.
- Grafana API подтвердил ClickHouse datasource.
- Grafana API подтвердил dashboard `Online Gallery Real-time Activity`.
- Airflow CLI подтвердил DAG `gallery_raw_ingestion`.
- Airflow import errors: `No data found`.

## 11. Исправления после первичного запуска

Во время проверки локального запуска были выявлены и исправлены проблемы:

1. `webapp` падал из-за `npm install` и сетевой ошибки `ECONNRESET`.
   Исправление: добавлен `webapp/server.js` и статическая демо-витрина `webapp/static`.

2. Grafana падала при попытке скачать ClickHouse plugin с `grafana.com`.
   Исправление: plugin установлен и сохранён локально в `grafana/plugins`.

3. Cube писал `Model files not found`.
   Исправление: добавлен каталог `cube/model`.

4. `airflow-init` падал на аргументе `--if-not-exists`.
   Исправление: команда создания пользователя изменена.

5. Пользователь Airflow отсутствовал после неудачного init.
   Исправление: пользователь `admin/admin` создан и проверен.

## 12. Ограничения

Есть несколько ограничений текущего локального стенда:

- Terraform CLI не установлен локально, поэтому `terraform validate` не выполнялся в этой среде.
- `pytest` в системном Python не запускался, потому что локально не установлены `pandas` и `pytest`.
- Flink image тяжёлый, поэтому для обычной демонстрации сайта его лучше не запускать.
- Реальный cloud deploy требует заполнения `terraform/terraform.tfvars` настоящими Yandex Cloud credentials.
- Реальные Telegram/Slack alerts требуют токенов в `.env`.

## 13. Сценарий защиты

Рекомендуемый порядок демонстрации:

1. Открыть `http://localhost:5173` и показать embedded analytics UI.
2. Нажать на выставку и показать drill-down до возрастных групп.
3. Открыть Airflow `http://localhost:8080` и показать DAG `gallery_raw_ingestion`.
4. Открыть Grafana `http://localhost:3000` и показать dashboard `Online Gallery Real-time Activity`.
5. Открыть Cube `http://localhost:4000` и объяснить semantic layer.
6. Показать ClickHouse таблицы и Gold-слой.
7. Показать Terraform в папке `terraform`.
8. Показать Data Product в `docs/data-products/artwork_engagement.md`.
9. Показать CI/CD pipeline в `.gitlab-ci.yml`.
10. Показать ADR и документацию в `docs`.

## 14. Итог

Работа выполнена как полный проект data platform для онлайн-галереи юных художников. Реализованы все части задания: домены данных, Terraform, Airflow, Raw ingestion, Great Expectations, lineage, Lakehouse, Feature Store, streaming pipeline, ClickHouse, Grafana, Cube semantic layer, embedded analytics UI, GitLab CI/CD и документация.

Локальная демонстрация работает вне виртуальной машины. Главная точка входа:

`http://localhost:5173`
