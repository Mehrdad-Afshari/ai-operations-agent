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
