from __future__ import annotations

import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from edu_platform.config import PlatformConfig


def build_spark(config: PlatformConfig) -> SparkSession:
    warehouse = f"s3a://{config.s3_bucket}/lakehouse"
    builder = (
        SparkSession.builder.appName("edu-gallery-iceberg-lakehouse")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.gallery", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.gallery.type", "hadoop")
        .config("spark.sql.catalog.gallery.warehouse", warehouse)
        .config("spark.hadoop.fs.s3a.endpoint", config.s3_endpoint_url or "https://storage.yandexcloud.net")
        .config("spark.hadoop.fs.s3a.access.key", config.s3_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", config.s3_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    )
    return builder.getOrCreate()


def main() -> None:
    config = PlatformConfig.from_env()
    run_date = os.getenv("RUN_DATE", "*")
    spark = build_spark(config)

    submissions_raw = (
        f"s3a://{config.s3_bucket}/raw/gallery_engagement/artwork_submissions/ingestion_date={run_date}/*.parquet"
    )
    profiles_raw = f"s3a://{config.s3_bucket}/raw/young_artist_profile/artist_profiles/ingestion_date={run_date}/*.parquet"

    bronze_submissions = spark.read.parquet(submissions_raw)
    bronze_profiles = spark.read.parquet(profiles_raw)

    bronze_submissions.writeTo("gallery.bronze_artwork_submissions").using("iceberg").createOrReplace()
    bronze_profiles.writeTo("gallery.bronze_artist_profiles").using("iceberg").createOrReplace()

    silver_submissions = (
        bronze_submissions.dropDuplicates(["submission_id"])
        .filter((F.col("artist_age") >= 6) & (F.col("artist_age") <= 17))
        .filter((F.col("moderation_score") >= 0) & (F.col("moderation_score") <= 100))
        .withColumn("submitted_at_ts", F.to_timestamp("submitted_at"))
    )
    silver_profiles = bronze_profiles.dropDuplicates(["artist_id"]).filter((F.col("age") >= 6) & (F.col("age") <= 17))

    silver_submissions.writeTo("gallery.silver_artwork_submissions").using("iceberg").createOrReplace()
    silver_profiles.writeTo("gallery.silver_artist_profiles").using("iceberg").createOrReplace()

    gold_daily = (
        silver_submissions.withColumn("event_date", F.to_date("submitted_at_ts"))
        .groupBy("event_date", "category", "technique")
        .agg(
            F.count("submission_id").alias("submissions_count"),
            F.sum(F.col("is_published").cast("int")).alias("published_count"),
            F.avg("moderation_score").alias("avg_moderation_score"),
            F.countDistinct("artist_id").alias("active_artists"),
        )
    )
    gold_daily.writeTo("gallery.gold_artwork_engagement_daily").using("iceberg").createOrReplace()

    artist_features = (
        silver_submissions.groupBy("artist_id")
        .agg(
            F.count("submission_id").alias("total_submissions"),
            F.sum(F.col("is_published").cast("int")).alias("published_submissions"),
            F.avg("moderation_score").alias("avg_moderation_score"),
            F.countDistinct("category").alias("unique_categories"),
            F.max("submitted_at_ts").alias("event_timestamp"),
        )
        .withColumn("publication_rate", F.col("published_submissions") / F.col("total_submissions"))
        .join(silver_profiles, on="artist_id", how="left")
        .select(
            "artist_id",
            "event_timestamp",
            "age",
            "age_group",
            "region",
            "mentor_type",
            "total_submissions",
            "published_submissions",
            "publication_rate",
            "avg_moderation_score",
            "unique_categories",
        )
    )
    artist_features.writeTo("gallery.gold_artist_features").using("iceberg").createOrReplace()

    spark.stop()


if __name__ == "__main__":
    main()

