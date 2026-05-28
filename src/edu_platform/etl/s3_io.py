from __future__ import annotations

from io import BytesIO

import boto3
import pandas as pd

from edu_platform.config import PlatformConfig


def s3_client(config: PlatformConfig):
    return boto3.client(
        "s3",
        endpoint_url=config.s3_endpoint_url,
        aws_access_key_id=config.s3_access_key,
        aws_secret_access_key=config.s3_secret_key,
        region_name=config.s3_region,
    )


def put_dataframe_as_parquet(df: pd.DataFrame, bucket: str, key: str, config: PlatformConfig) -> str:
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    s3_client(config).put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    return f"s3://{bucket}/{key}"

