# Архитектура решения

```mermaid
flowchart LR
  API[Old Gallery API] --> Airflow
  CSV[Admin CSV exports] --> Airflow
  Airflow --> GX[Great Expectations]
  GX --> S3[(S3/Object Storage Raw)]
  S3 --> Spark[Spark + Iceberg]
  Spark --> Bronze[Bronze]
  Bronze --> Silver[Silver]
  Silver --> Gold[Gold]
  Gold --> Feast[Feast Feature Store]
  Gold --> ClickHouse[(ClickHouse)]
  Web[Gallery web events] --> Kafka[(Managed Kafka)]
  Kafka --> Flink[Flink window aggregation]
  Flink --> KafkaAgg[Kafka aggregate topic]
  KafkaAgg --> ClickHouse
  ClickHouse --> Grafana
  ClickHouse --> Cube[Cube Semantic Layer]
  Cube --> React[Embedded React analytics]
```

## Ключевые решения

- Object Storage используется как S3-compatible Data Lake.
- Kafka отделяет генерацию событий сайта от real-time обработки.
- Airflow отвечает за batch orchestration, retry и алерты.
- Great Expectations задаёт контракты качества для Raw слоя.
- Iceberg обеспечивает ACID-таблицы Bronze/Silver/Gold поверх S3.
- Feast регистрирует Gold-признаки для ML-сценариев.
- Cube отделяет бизнес-метрики от физических таблиц ClickHouse.
