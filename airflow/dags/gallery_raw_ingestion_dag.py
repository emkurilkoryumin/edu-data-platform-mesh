from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from edu_platform.utils.alerts import notify_failure


def run_load_artwork_submissions_raw(run_date: str | None = None) -> dict[str, str]:
    from edu_platform.etl.raw_loader import load_artwork_submissions_raw

    return load_artwork_submissions_raw(run_date=run_date)


def run_load_artist_profiles_raw(run_date: str | None = None) -> dict[str, str]:
    from edu_platform.etl.raw_loader import load_artist_profiles_raw

    return load_artist_profiles_raw(run_date=run_date)


default_args = {
    "owner": "gallery-data-platform",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
    "on_failure_callback": notify_failure,
}


with DAG(
    dag_id="gallery_raw_ingestion",
    description="Load old gallery API and CSV exports to S3 raw parquet with quality gates.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data_mesh", "gallery", "raw", "great_expectations"],
) as dag:
    load_api_submissions = PythonOperator(
        task_id="load_artwork_submissions_raw",
        python_callable=run_load_artwork_submissions_raw,
        op_kwargs={"run_date": "{{ ds }}"},
    )

    load_csv_profiles = PythonOperator(
        task_id="load_artist_profiles_raw",
        python_callable=run_load_artist_profiles_raw,
        op_kwargs={"run_date": "{{ ds }}"},
    )

    [load_api_submissions, load_csv_profiles]
