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

variable "enable_deletion_protection" {
  description = "Protect the database from accidental deletion in long-lived environments."
  type        = bool
  default     = false
}
