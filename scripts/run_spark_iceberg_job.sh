#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

spark-submit \
  --packages "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.hadoop:hadoop-aws:3.3.4" \
  src/edu_platform/lakehouse/spark_iceberg_job.py
