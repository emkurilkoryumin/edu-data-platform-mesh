# ADR 0001: Domain-oriented data platform for online gallery

## Status

Accepted.

## Context

Старый сайт был онлайн-галереей юных художников. Для задания нужна не просто локальная
инсталляция инструментов, а облачная основа платформы с Data Mesh, Lakehouse, streaming,
semantic layer и CI/CD.

## Decision

Строим доменно-ориентированную платформу:

- Yandex Cloud как целевой cloud provider для Terraform.
- Object Storage как S3-compatible lake.
- Managed Kafka для событий сайта.
- VM с Docker Compose для Airflow и вспомогательных сервисов.
- Apache Iceberg поверх S3 для Bronze/Silver/Gold.
- ClickHouse для real-time и BI serving.
- Cube как semantic layer.
- React как embedded analytics UI.

## Consequences

- Решение разворачивается локально через Docker Compose и в облаке через Terraform.
- Секреты передаются через `.env`, Terraform variables и GitLab CI variables.
- Для production нужно заменить публичные ingress CIDR на allowlist и вынести секреты в Secret Manager.
