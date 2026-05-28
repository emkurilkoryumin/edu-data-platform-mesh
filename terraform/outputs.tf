output "bucket_name" {
  description = "Object Storage bucket used as S3-compatible data lake."
  value       = yandex_storage_bucket.lake.bucket
}

output "orchestrator_public_ip" {
  description = "Public IP address of Docker orchestration VM."
  value       = yandex_compute_instance.orchestrator.network_interface[0].nat_ip_address
}

output "airflow_url" {
  description = "Airflow web UI URL."
  value       = "http://${yandex_compute_instance.orchestrator.network_interface[0].nat_ip_address}:8080"
}

output "grafana_url" {
  description = "Grafana web UI URL."
  value       = "http://${yandex_compute_instance.orchestrator.network_interface[0].nat_ip_address}:3000"
}

output "kafka_cluster_id" {
  description = "Managed Kafka cluster ID."
  value       = yandex_mdb_kafka_cluster.events.id
}

output "kafka_topics" {
  description = "Kafka topics created for batch lineage and streaming."
  value = [
    yandex_mdb_kafka_topic.gallery_events.name,
    yandex_mdb_kafka_topic.gallery_occupancy_5m.name
  ]
}
