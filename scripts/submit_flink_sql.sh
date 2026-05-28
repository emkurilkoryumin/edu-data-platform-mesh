#!/usr/bin/env bash
set -euo pipefail

docker compose exec flink-jobmanager /opt/flink/bin/sql-client.sh \
  -f /opt/flink/sql/gallery_window_aggregation.sql
