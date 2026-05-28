locals {
  bucket_name = coalesce(var.bucket_name, "${var.platform_name}-${var.environment}-lake")
  labels = {
    project     = var.platform_name
    environment = var.environment
  }
}

resource "yandex_vpc_network" "platform" {
  name   = "${var.platform_name}-${var.environment}-net"
  labels = local.labels
}

resource "yandex_vpc_subnet" "platform" {
  name           = "${var.platform_name}-${var.environment}-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.platform.id
  v4_cidr_blocks = ["10.20.0.0/24"]
  labels         = local.labels
}

resource "yandex_vpc_security_group" "vm" {
  name       = "${var.platform_name}-${var.environment}-vm-sg"
  network_id = yandex_vpc_network.platform.id
  labels     = local.labels

  ingress {
    description    = "SSH"
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = var.trusted_cidr_blocks
  }

  ingress {
    description    = "Airflow UI"
    protocol       = "TCP"
    port           = 8080
    v4_cidr_blocks = var.trusted_cidr_blocks
  }

  ingress {
    description    = "Grafana"
    protocol       = "TCP"
    port           = 3000
    v4_cidr_blocks = var.trusted_cidr_blocks
  }

  ingress {
    description    = "Cube API"
    protocol       = "TCP"
    port           = 4000
    v4_cidr_blocks = var.trusted_cidr_blocks
  }

  egress {
    description    = "Outbound internet"
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_iam_service_account" "storage" {
  name        = "${var.platform_name}-${var.environment}-storage"
  description = "Service account for Object Storage lakehouse access."
  labels      = local.labels
}

resource "yandex_resourcemanager_folder_iam_member" "storage_editor" {
  folder_id = var.folder_id
  role      = "storage.editor"
  member    = "serviceAccount:${yandex_iam_service_account.storage.id}"
}

resource "yandex_iam_service_account_static_access_key" "storage" {
  service_account_id = yandex_iam_service_account.storage.id
  description        = "S3 static key for gallery data lake."
}

resource "yandex_storage_bucket" "lake" {
  bucket     = local.bucket_name
  access_key = yandex_iam_service_account_static_access_key.storage.access_key
  secret_key = yandex_iam_service_account_static_access_key.storage.secret_key
  acl        = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "raw-retention"
    enabled = true
    prefix  = "raw/"

    expiration {
      days = 365
    }
  }

  depends_on = [yandex_resourcemanager_folder_iam_member.storage_editor]
}

resource "yandex_mdb_kafka_cluster" "events" {
  name        = "${var.platform_name}-${var.environment}-kafka"
  environment = var.environment == "prod" ? "PRODUCTION" : "PRESTABLE"
  network_id  = yandex_vpc_network.platform.id
  subnet_ids  = [yandex_vpc_subnet.platform.id]
  labels      = local.labels

  config {
    version       = "3.6"
    brokers_count = var.kafka_brokers_count
    zones         = [var.zone]

    kafka {
      resources {
        resource_preset_id = "s2.micro"
        disk_type_id       = "network-ssd"
        disk_size          = 20
      }
    }
  }
}

resource "yandex_mdb_kafka_topic" "gallery_events" {
  cluster_id         = yandex_mdb_kafka_cluster.events.id
  name               = "gallery.events"
  partitions         = 3
  replication_factor = 1
}

resource "yandex_mdb_kafka_topic" "gallery_occupancy_5m" {
  cluster_id         = yandex_mdb_kafka_cluster.events.id
  name               = "gallery.occupancy_5m"
  partitions         = 3
  replication_factor = 1
}

resource "yandex_mdb_kafka_user" "app" {
  cluster_id = yandex_mdb_kafka_cluster.events.id
  name       = "gallery_app"
  password   = var.kafka_user_password

  permission {
    topic_name = "gallery.events"
    role       = "ACCESS_ROLE_PRODUCER"
  }

  permission {
    topic_name = "gallery.events"
    role       = "ACCESS_ROLE_CONSUMER"
  }

  permission {
    topic_name = "gallery.occupancy_5m"
    role       = "ACCESS_ROLE_PRODUCER"
  }

  permission {
    topic_name = "gallery.occupancy_5m"
    role       = "ACCESS_ROLE_CONSUMER"
  }
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_compute_instance" "orchestrator" {
  name        = "${var.platform_name}-${var.environment}-orchestrator"
  platform_id = "standard-v3"
  zone        = var.zone
  labels      = local.labels

  resources {
    cores         = var.vm_cores
    memory        = var.vm_memory_gb
    core_fraction = 50
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = var.vm_disk_gb
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.platform.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.vm.id]
  }

  metadata = {
    ssh-keys  = "ubuntu:${file(pathexpand(var.ssh_public_key_path))}"
    user-data = templatefile("${path.module}/templates/cloud-init.yaml.tftpl", {
      platform_name       = var.platform_name
      environment         = var.environment
      s3_endpoint_url     = "https://storage.yandexcloud.net"
      s3_bucket           = yandex_storage_bucket.lake.bucket
      s3_access_key       = yandex_iam_service_account_static_access_key.storage.access_key
      s3_secret_key       = yandex_iam_service_account_static_access_key.storage.secret_key
      s3_region           = "ru-central1"
      kafka_bootstrap     = "c-${yandex_mdb_kafka_cluster.events.id}.rw.mdb.yandexcloud.net:9091"
      kafka_username      = yandex_mdb_kafka_user.app.name
      kafka_password      = var.kafka_user_password
      telegram_bot_token  = var.telegram_bot_token
      telegram_chat_id    = var.telegram_chat_id
      slack_webhook_url   = var.slack_webhook_url
    })
  }
}
