from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformConfig:
    project_name: str
    environment: str
    s3_endpoint_url: str | None
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    s3_region: str
    kafka_bootstrap_servers: str
    clickhouse_host: str
    clickhouse_port: int
    clickhouse_database: str

    @classmethod
    def from_env(cls) -> "PlatformConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "edu-gallery-platform"),
            environment=os.getenv("ENVIRONMENT", "local"),
            s3_endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
            s3_bucket=os.getenv("S3_BUCKET", "edu-gallery-lake"),
            s3_access_key=os.getenv("S3_ACCESS_KEY", "gallery"),
            s3_secret_key=os.getenv("S3_SECRET_KEY", "gallery-secret"),
            s3_region=os.getenv("S3_REGION", "ru-central1"),
            kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            clickhouse_host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            clickhouse_port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
            clickhouse_database=os.getenv("CLICKHOUSE_DATABASE", "gallery"),
        )

