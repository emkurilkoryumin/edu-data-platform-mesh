variable "cloud_id" {
  description = "Yandex Cloud ID."
  type        = string
}

variable "folder_id" {
  description = "Yandex Cloud folder ID."
  type        = string
}

variable "zone" {
  description = "Yandex Cloud availability zone."
  type        = string
  default     = "ru-central1-a"
}

variable "platform_name" {
  description = "Name prefix for all platform resources."
  type        = string
  default     = "edu-gallery-platform"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "stage"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key for VM access."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "trusted_cidr_blocks" {
  description = "CIDR blocks allowed to connect to VM services."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "bucket_name" {
  description = "Globally unique Object Storage bucket name. Leave null to generate from platform_name."
  type        = string
  default     = null
}

variable "vm_cores" {
  description = "VM CPU cores for Docker orchestration host."
  type        = number
  default     = 2
}

variable "vm_memory_gb" {
  description = "VM RAM in GB."
  type        = number
  default     = 4
}

variable "vm_disk_gb" {
  description = "VM boot disk size in GB."
  type        = number
  default     = 35
}

variable "kafka_brokers_count" {
  description = "Number of managed Kafka brokers."
  type        = number
  default     = 1
}

variable "kafka_user_password" {
  description = "Password for managed Kafka application user."
  type        = string
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Optional Telegram bot token for Airflow failure alerts."
  type        = string
  default     = ""
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Optional Telegram chat id for Airflow failure alerts."
  type        = string
  default     = ""
  sensitive   = true
}

variable "slack_webhook_url" {
  description = "Optional Slack webhook URL for Airflow failure alerts."
  type        = string
  default     = ""
  sensitive   = true
}
