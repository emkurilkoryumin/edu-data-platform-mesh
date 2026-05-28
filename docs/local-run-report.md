# Отчёт: проверка локального запуска

Дата проверки: 22 мая 2026.
Проект: `edu-data-platform-mesh`.
Кейс: онлайн-галерея юных художников.

## Что было не так

1. `webapp` не открывался на `http://localhost:5173`, потому что контейнер выполнял `npm install` при старте и падал из-за сетевой ошибки `ECONNRESET`.
2. `grafana` не открывалась на `http://localhost:3000`, потому что пыталась скачать `grafana-clickhouse-datasource` при старте и падала по таймауту доступа к `grafana.com`.
3. `cube` запускался, но писал `Model files not found`, потому что текущая версия Cube ожидает каталог `model`, а в проекте был только `schema`.
4. `airflow-init` падал на аргументе `--if-not-exists`, которого нет в установленной версии Airflow CLI.
5. Пользователь Airflow `admin` отсутствовал после первого неудачного init.

## Что исправлено

1. `webapp` переведён на встроенный Node HTTP server `webapp/server.js`, который открывает статическую демо-витрину без `npm install`.
2. Для задания React-исходники оставлены в `webapp/src`, а локальная демо-страница лежит в `webapp/static` и открывается сразу.
3. ClickHouse-плагин Grafana установлен и сохранён в `grafana/plugins/grafana-clickhouse-datasource`, затем подключён в `docker-compose.yml` как volume.
4. Cube model продублирован в `cube/model`, Dockerfile Cube обновлён на `COPY model /cube/conf/model`.
5. Airflow init-команда исправлена: удалён неподдерживаемый `--if-not-exists`, добавлен безопасный `|| true` для повторного запуска.
6. Пользователь Airflow `admin/admin` создан и проверен через `airflow users list`.

## Проверенный статус сервисов

Все основные контейнеры подняты:

- `airflow-webserver` на порту `8080`.
- `airflow-scheduler`.
- `airflow-postgres`.
- `airflow-redis`.
- `minio` на портах `9000` и `9001`.
- `kafka` на порту `9092`.
- `zookeeper`.
- `clickhouse` на портах `8123` и `9002`.
- `cube` на порту `4000`.
- `grafana` на порту `3000`.
- `webapp` на порту `5173`.

## Проверенные локальные адреса

- `http://localhost:5173` возвращает `HTTP/1.1 200 OK`.
- `http://localhost:3000` возвращает `HTTP/1.1 200 OK` после редиректа на `/login`.
- `http://localhost:8080` отвечает редиректом Airflow на `/home` и открывается в браузере.
- `http://localhost:4000` возвращает `HTTP/1.1 200 OK`.
- `http://localhost:9001` возвращает `HTTP/1.1 200 OK`.
- `http://localhost:8123/?query=SELECT%201` возвращает `1`.

## Проверка данных и аналитики

1. ClickHouse содержит таблицы:
   - `gallery_occupancy_5m`
   - `gallery_occupancy_5m_mv`
   - `gallery_occupancy_5m_queue`
   - `gold_artwork_engagement_daily`

2. В `gallery.gold_artwork_engagement_daily` есть 3 демонстрационные записи.

3. Cube API успешно вернул метрики из ClickHouse:
   - `animals_and_friends`: 1470 просмотров
   - `spring_colors`: 1200 просмотров
   - `digital_future`: 980 просмотров

4. Grafana API подтвердил datasource:
   - name: `ClickHouse`
   - type: `grafana-clickhouse-datasource`
   - url: `http://clickhouse:8123`

5. Grafana API подтвердил dashboard:
   - `Online Gallery Real-time Activity`
   - URL: `/d/gallery-realtime/online-gallery-real-time-activity`

6. Airflow подтвердил DAG:
   - `gallery_raw_ingestion`
   - import errors: `No data found`

## Как открыть локально

```bash
cd /home/emkurilkoryumin/edu-data-platform-mesh
docker compose up -d
```

Открыть в браузере:

- Главная демо-витрина: http://localhost:5173
- Airflow: http://localhost:8080, `admin/admin`
- Grafana: http://localhost:3000, `admin/admin`
- Cube: http://localhost:4000
- MinIO: http://localhost:9001, `gallery/gallery-secret`

## Итог

Проект теперь можно открыть локально вне виртуальной машины. Основная демонстрация начинается с `http://localhost:5173`; оттуда есть ссылки на Airflow, Grafana, Cube и MinIO.

## Ограничения проверки

`pytest` в системном Python не запускался, потому что в локальном окружении вне Docker не установлены `pandas` и `pytest`. Синтаксис Python проверен через `python3 -m compileall`; runtime-сервисы проверены через Docker Compose и HTTP/API-запросы.
