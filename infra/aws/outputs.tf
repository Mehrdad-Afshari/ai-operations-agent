output "vpc_id" {
  description = "ID of the application VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs reserved for internet-facing ingress."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs reserved for application and data services."
  value       = aws_subnet.private[*].id
}

output "backend_ecr_repository_url" {
  description = "ECR repository URL for the backend image."
  value       = aws_ecr_repository.backend.repository_url
}

output "api_url" {
  description = "HTTP endpoint of the portfolio API load balancer."
  value       = "http://${aws_lb.api.dns_name}"
}

output "ecs_cluster_name" {
  description = "ECS cluster used by the API and worker services."
  value       = aws_ecs_cluster.main.name
}

output "database_endpoint" {
  description = "Private RDS endpoint for operational diagnostics."
  value       = aws_db_instance.postgres.address
}
