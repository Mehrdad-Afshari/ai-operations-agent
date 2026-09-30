variable "aws_region" {
  description = "AWS region used for the deployment."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Base name used for AWS resources."
  type        = string
  default     = "ai-operations-agent"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "portfolio"
}

variable "image_tag" {
  description = "Immutable ECR image tag deployed to ECS."
  type        = string
  default     = "bootstrap"
}

variable "db_name" {
  description = "PostgreSQL application database name."
  type        = string
  default     = "operations_agent"
}

variable "db_username" {
  description = "PostgreSQL application username."
  type        = string
  default     = "operations_agent"
}

variable "db_password" {
  description = "PostgreSQL application password. Supply through TF_VAR_db_password or a secure deployment system."
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type."
  type        = string
  default     = "cache.t4g.micro"
}

variable "api_cpu" {
  description = "Fargate CPU units for the API task."
  type        = number
  default     = 256
}

variable "api_memory" {
  description = "Fargate memory MiB for the API task."
  type        = number
  default     = 512
}

variable "worker_cpu" {
  description = "Fargate CPU units for the worker task."
  type        = number
  default     = 256
}

variable "worker_memory" {
  description = "Fargate memory MiB for the worker task."
  type        = number
  default     = 512
}

variable "api_desired_count" {
  description = "Number of API tasks."
  type        = number
  default     = 1
}

variable "worker_desired_count" {
  description = "Number of Celery worker tasks."
  type        = number
  default     = 1
}

variable "enable_deletion_protection" {
  description = "Protect the database from accidental deletion in long-lived environments."
  type        = bool
  default     = false
}
