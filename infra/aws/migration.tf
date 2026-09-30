resource "aws_cloudwatch_log_group" "migration" {
  name              = "/ecs/${local.name}/migration"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "migration" {
  family                   = "${local.name}-migration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([{
    name        = "migration"
    image       = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
    essential   = true
    command     = ["alembic", "upgrade", "head"]
    environment = local.runtime_environment
    secrets     = local.runtime_secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.migration.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "migration"
      }
    }
  }])
}

output "migration_task_definition_arn" {
  description = "Task definition to run before rolling out API and worker services."
  value       = aws_ecs_task_definition.migration.arn
}
