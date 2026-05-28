# Объяснение проекта и структуры

Проект `edu-data-platform-mesh` - это учебная data platform для старого сайта, который был онлайн-галереей юных художников. Идея проекта: показать, как из обычного сайта можно построить полноценную платформу данных с загрузкой данных, проверкой качества, аналитическими слоями, real-time событиями, дашбордами, semantic layer и CI/CD.

Главная локальная точка входа для демонстрации:

`http://localhost:5173`

## 1. Что делает проект

Проект моделирует работу онлайн-галереи:

- юные художники регистрируются на сайте;
- художники загружают свои работы;
- работы проходят модерацию;
- посетители смотрят виртуальные выставки;
- посетители лайкают работы, пишут комментарии и переходят между залами;
- платформа собирает данные и строит аналитику.

На основе этих данных реализованы:

- batch-загрузка данных в Data Lake;
- проверка качества данных;
- lineage, то есть фиксация пути данных от источника до витрины;
- lakehouse-слои Bronze, Silver и Gold;
- feature store для ML-признаков;
- потоковая обработка событий;
- real-time dashboard;
- semantic layer;
- embedded analytics интерфейс;
- CI/CD pipeline.

## 2. Общая логика движения данных

Данные проходят такой путь:

1. Источники данных:
   - симулированный API старого сайта галереи;
   - CSV-выгрузка профилей юных художников;
   - события сайта в Kafka.

2. Raw layer:
   - Airflow запускает загрузку;
   - данные проверяются Great Expectations;
   - после проверки сохраняются в S3-compatible хранилище в формате Parquet.

3. Lakehouse:
   - Spark читает Raw-данные;
   - создаёт Bronze слой;
   - очищает данные в Silver;
   - строит Gold-агрегаты и признаки.

4. Serving layer:
   - Gold-таблицы и real-time агрегаты попадают в ClickHouse;
   - Cube.js описывает бизнес-метрики поверх таблиц;
   - Grafana строит real-time dashboard;
   - Web UI показывает embedded analytics.

5. CI/CD:
   - GitLab CI проверяет код;
   - запускает тесты;
   - проверяет качество данных;
   - собирает Docker-образы;
   - деплоит на стенд.

## 3. Главные компоненты проекта

## 3.1. Terraform

Папка:

`terraform/`

За что отвечает:

- создаёт облачную инфраструктуру в Yandex Cloud;
- создаёт Object Storage bucket;
- создаёт Managed Kafka;
- создаёт VM;
- создаёт сеть, subnet и security group;
- создаёт Kafka topics;
- через cloud-init поднимает Airflow в Docker на VM.

Главные файлы:

- `terraform/main.tf` - основные ресурсы Yandex Cloud;
- `terraform/variables.tf` - входные переменные;
- `terraform/outputs.tf` - выходные значения после деплоя;
- `terraform/versions.tf` - версии Terraform provider;
- `terraform/terraform.tfvars.example` - пример переменных;
- `terraform/templates/cloud-init.yaml.tftpl` - bootstrap VM.

Смысл этой части: показать, что платформа может разворачиваться не вручную, а как Infrastructure as Code.

## 3.2. Docker Compose

Файл:

`docker-compose.yml`

За что отвечает:

- поднимает локальный стенд для демонстрации;
- запускает MinIO, Kafka, ClickHouse, Airflow, Cube, Grafana и web UI;
- позволяет открыть проект без облачной VM.

Основные сервисы:

- `minio` - локальный аналог S3;
- `kafka` - брокер событий;
- `clickhouse` - аналитическая колоночная БД;
- `airflow-webserver` - UI Airflow;
- `airflow-scheduler` - планировщик DAG;
- `cube` - semantic layer;
- `grafana` - dashboard;
- `webapp` - локальная витрина проекта.

Главный локальный сайт:

`http://localhost:5173`

## 3.3. Airflow

Папка:

`airflow/dags/`

Главный файл:

`airflow/dags/gallery_raw_ingestion_dag.py`

За что отвечает:

- запускает batch pipeline;
- загружает данные из симулированного API;
- загружает данные из CSV;
- запускает проверки качества;
- пишет данные в Raw слой;
- использует retry;
- при ошибках может отправлять алерты в Telegram или Slack.

Airflow нужен для оркестрации: он показывает, какие задачи выполняются, в каком порядке, когда упали и сколько было retry.

## 3.4. ETL-код

Папка:

`src/edu_platform/etl/`

Главные файлы:

- `gallery_sources.py`
- `raw_loader.py`
- `s3_io.py`

За что отвечают:

- `gallery_sources.py` генерирует данные старого сайта галереи;
- `raw_loader.py` выполняет загрузку данных в Raw layer;
- `s3_io.py` отвечает за запись DataFrame в S3-compatible storage в формате Parquet.

Эта часть имитирует реальные источники данных старого сайта.

## 3.5. Great Expectations и качество данных

Папка:

`great_expectations/`

Главные файлы:

- `great_expectations/expectations/raw_artwork_submissions.json`
- `great_expectations/expectations/raw_artist_profiles.json`
- `src/edu_platform/quality/validate_raw.py`

За что отвечает:

- проверяет, что ключи не пустые;
- проверяет, что ключи уникальны;
- проверяет возраст художника;
- проверяет moderation score;
- проверяет допустимые значения техник и возрастных групп.

Примеры проверок:

- `submission_id` должен быть уникальным;
- `artist_age` должен быть от 6 до 17;
- `moderation_score` должен быть от 0 до 100;
- `age_group` должен быть одним из `6-9`, `10-13`, `14-17`.

Смысл этой части: плохие данные не должны попадать дальше в lakehouse и аналитику.

## 3.6. Data Lineage

Папка:

`metadata/`

Главные файлы:

- `metadata/lineage.yml`
- `src/edu_platform/lineage/emit_lineage.py`

За что отвечает:

- описывает, откуда пришли данные;
- показывает, какие Raw datasets получаются из каких источников;
- показывает переходы Raw -> Bronze -> Silver -> Gold;
- сохраняет runtime lineage events.

Lineage нужен, чтобы понимать путь данных и объяснять происхождение каждой витрины.

## 3.7. Lakehouse

Папка:

`src/edu_platform/lakehouse/`

Главные файлы:

- `spark_iceberg_job.py`
- `transforms.py`
- `metadata/lakehouse/gallery_gold.sql`

За что отвечает:

- строит Bronze, Silver и Gold слои;
- использует Apache Iceberg как формат таблиц;
- очищает данные;
- строит агрегаты;
- формирует таблицу признаков для ML.

Слои:

- Bronze - сырые данные, почти без изменений;
- Silver - очищенные и дедуплицированные данные;
- Gold - готовые агрегаты и признаки для аналитики и ML.

## 3.8. Feature Store

Папка:

`feast/feature_repo/`

Главные файлы:

- `feature_store.yaml`
- `features.py`

За что отвечает:

- регистрирует entity `artist`;
- регистрирует feature view `artist_artwork_features`;
- описывает признаки художника для ML.

Примеры признаков:

- возраст;
- возрастная группа;
- регион;
- тип наставника;
- количество загруженных работ;
- доля опубликованных работ;
- средний moderation score;
- количество уникальных категорий.

Смысл Feature Store: ML-модель может брать признаки из единого стандартизированного места.

## 3.9. Streaming

Папки:

- `src/edu_platform/streaming/`
- `flink/sql/`

Главные файлы:

- `src/edu_platform/streaming/gallery_event_generator.py`
- `flink/sql/gallery_window_aggregation.sql`

За что отвечает:

- генератор создаёт события сайта;
- события отправляются в Kafka topic `gallery.events`;
- Flink агрегирует события в окна;
- результат записывается в `gallery.occupancy_5m`.

Примеры событий:

- просмотр работы;
- лайк;
- комментарий;
- начало загрузки работы;
- вход в виртуальный зал.

Пример real-time метрики:

- количество активных посетителей в виртуальном зале за последние 5 минут.

## 3.10. ClickHouse

Папка:

`clickhouse/init/`

Главный файл:

`clickhouse/init/001_gallery_schema.sql`

За что отвечает:

- создаёт БД `gallery`;
- создаёт таблицы для real-time агрегатов;
- создаёт Kafka queue table;
- создаёт materialized view;
- создаёт демонстрационную Gold-таблицу для аналитики.

ClickHouse нужен как быстрый аналитический слой для Grafana и Cube.

## 3.11. Grafana

Папки:

- `grafana/dashboards/`
- `grafana/provisioning/`
- `grafana/plugins/`

Главные файлы:

- `grafana/dashboards/gallery_realtime.json`
- `grafana/provisioning/datasources/clickhouse.yml`

За что отвечает:

- показывает real-time dashboard;
- подключается к ClickHouse;
- отображает активность виртуальных выставок.

Локальный адрес:

`http://localhost:3000`

Логин и пароль:

`admin/admin`

## 3.12. Cube.js

Папки:

- `cube/schema/`
- `cube/model/`

Главные файлы:

- `ArtworkEngagement.js`
- `RoomUtilization.js`

За что отвечает:

- отделяет бизнес-логику от физических таблиц;
- описывает бизнес-метрики;
- даёт API для веб-интерфейса.

Примеры метрик:

- `StudentCount`;
- `ArtworkCount`;
- `Views`;
- `Likes`;
- `AvgGrade`;
- `RoomUtilization`.

Cube нужен, чтобы frontend не писал SQL напрямую и не зависел от структуры таблиц ClickHouse.

## 3.13. Web UI

Папка:

`webapp/`

Главные файлы:

- `webapp/src/App.jsx` - React-версия интерфейса;
- `webapp/static/index.html` - локальная демо-страница;
- `webapp/static/app.js` - логика drill-down;
- `webapp/static/styles.css` - стили;
- `webapp/server.js` - простой Node server.

За что отвечает:

- показывает embedded analytics;
- показывает графики по выставкам;
- позволяет сделать drill-down с выставки на возрастные группы.

Главный адрес:

`http://localhost:5173`

Именно этот адрес лучше открывать первым при демонстрации.

## 3.14. CI/CD

Файл:

`.gitlab-ci.yml`

За что отвечает:

- проверяет Python-код;
- запускает pytest;
- запускает quality checks;
- собирает Docker images;
- деплоит на staging через SSH.

Смысл этой части: показать, что проект можно автоматически проверять и разворачивать.

## 3.15. Тесты

Папка:

`tests/`

Файлы:

- `tests/test_quality_rules.py`
- `tests/test_lakehouse_transforms.py`

Что проверяют:

- quality rules проходят на корректных данных;
- дубликаты ключей ловятся проверками;
- feature transformations работают корректно;
- daily aggregation считает строки правильно.

## 3.16. Документация

Папка:

`docs/`

Главные файлы:

- `docs/final-work-report.md` - итоговый отчёт по всей работе;
- `docs/project-explanation.md` - этот файл с объяснением структуры;
- `docs/local-run-report.md` - отчёт о локальной проверке запуска;
- `docs/architecture.md` - архитектура;
- `docs/data-domains.md` - домены данных;
- `docs/requirements-mapping.md` - соответствие требований и файлов;
- `docs/deployment.md` - запуск и развёртывание;
- `docs/observability.md` - мониторинг, алерты, lineage;
- `docs/defense-demo.md` - сценарий защиты;
- `docs/adr/0001-domain-oriented-gallery-platform.md` - архитектурное решение;
- `docs/data-products/artwork_engagement.md` - описание Data Product.

## 4. Структура проекта

Общая структура:

```text
edu-data-platform-mesh/
├── airflow/
│   └── dags/
├── clickhouse/
│   └── init/
├── cube/
│   ├── model/
│   └── schema/
├── data/
│   └── sample/
├── docker/
│   └── airflow/
├── docs/
│   ├── adr/
│   └── data-products/
├── feast/
│   └── feature_repo/
├── flink/
│   └── sql/
├── grafana/
│   ├── dashboards/
│   ├── plugins/
│   └── provisioning/
├── great_expectations/
│   └── expectations/
├── metadata/
│   └── lakehouse/
├── scripts/
├── src/
│   └── edu_platform/
├── terraform/
│   └── templates/
├── tests/
└── webapp/
    ├── src/
    └── static/
```

## 5. Что показывать на защите

Рекомендуемый порядок:

1. Открыть `http://localhost:5173`.
2. Показать, что это embedded analytics для онлайн-галереи.
3. Нажать на выставку и показать drill-down.
4. Открыть `docs/data-domains.md` и показать домены данных.
5. Открыть `terraform/main.tf` и показать облачную инфраструктуру.
6. Открыть Airflow `http://localhost:8080` и показать DAG.
7. Показать Great Expectations expectations.
8. Показать lineage в `metadata/lineage.yml`.
9. Показать lakehouse job `spark_iceberg_job.py`.
10. Показать Feast features.
11. Открыть Grafana `http://localhost:3000`.
12. Открыть Cube schema и объяснить semantic layer.
13. Показать `.gitlab-ci.yml`.
14. Показать итоговый отчёт `docs/final-work-report.md`.

## 6. Как объяснить проект коротко

Короткое объяснение:

> Я взял кейс старого сайта онлайн-галереи юных художников и спроектировал вокруг него data platform. Сайт генерирует данные о художниках, работах, выставках и действиях посетителей. Airflow загружает данные в Raw слой, Great Expectations проверяет качество, Spark и Iceberg строят Lakehouse слои Bronze/Silver/Gold, Feast регистрирует признаки для ML, Kafka и Flink обрабатывают события в реальном времени, ClickHouse хранит аналитические витрины, Grafana показывает real-time dashboard, Cube.js задаёт semantic layer, а web UI показывает embedded analytics с drill-down. Вся инфраструктура описана Terraform, а проверки и деплой автоматизированы через GitLab CI/CD.

## 7. Как объяснить структуру одной фразой

Короткая фраза:

> В проекте каждая папка соответствует отдельному слою платформы: `terraform` отвечает за облако, `airflow` за оркестрацию, `src` за ETL и трансформации, `great_expectations` за качество, `metadata` за lineage, `feast` за Feature Store, `flink` и `kafka` за streaming, `clickhouse` за аналитическое хранилище, `grafana` за дашборды, `cube` за semantic layer, `webapp` за embedded analytics, а `docs` за защиту и документацию.

## 8. Локальный запуск

Главная команда для демонстрации сайта:

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
docker compose up -d webapp
```

Главная страница:

`http://localhost:5173`

Для демонстрации остальных компонентов:

```bash
docker compose up -d minio zookeeper kafka clickhouse cube grafana airflow-postgres airflow-redis airflow-webserver airflow-scheduler webapp
```

## 9. Что уже проверено

Проверено:

- web UI открывается на `http://localhost:5173`;
- Grafana открывается на `http://localhost:3000`;
- Cube API отвечает на `http://localhost:4000`;
- ClickHouse отвечает на `http://localhost:8123`;
- Airflow DAG присутствует;
- Grafana datasource ClickHouse настроен;
- Grafana dashboard импортирован;
- Cube возвращает данные из ClickHouse;
- Python-код компилируется;
- Docker Compose конфигурация валидна.

## 10. Итоговое понимание

Этот проект показывает не просто сайт, а полную data platform вокруг сайта. Старый сайт онлайн-галереи выступает источником данных. Платформа превращает эти данные в проверенные датасеты, аналитические витрины, ML-признаки, real-time метрики и встроенную аналитику для пользователей.

Главная ценность проекта в том, что все компоненты связаны в одну архитектуру и покрывают полный путь данных: от события на сайте до dashboard и бизнес-метрик.
