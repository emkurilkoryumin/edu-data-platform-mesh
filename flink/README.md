# Flink Streaming Job

`sql/gallery_window_aggregation.sql` читает Kafka topic `gallery.events`, агрегирует события
в hopping window `5 минут / шаг 1 минута` и пишет JSON в `gallery.occupancy_5m`.

Для локального запуска нужен Kafka SQL connector в `/opt/flink/lib`:

```bash
docker compose up -d kafka flink-jobmanager flink-taskmanager
./scripts/submit_flink_sql.sh
```

В Yandex Cloud topic создается Terraform-ом в Managed Kafka. Для production меняются
`properties.bootstrap.servers` и security settings в SQL.
