# AWS deployment architecture

This directory contains the Infrastructure as Code for the production deployment of AI Operations Agent.

## Target architecture

- **Amazon ECR** stores the versioned backend container image.
- **Amazon ECS on AWS Fargate** runs two independent services from the same image:
  - FastAPI API service
  - Celery worker service
- **Application Load Balancer** exposes only the API service and checks `/ready`.
- **Amazon RDS for PostgreSQL** stores requests, approval decisions, and audit events.
- **Amazon ElastiCache for Redis** provides the Celery broker/result backend.
- **AWS Secrets Manager** stores database and application secrets rather than committing credentials.
- **Amazon CloudWatch Logs** receives API and worker container logs.
- **VPC networking** separates public ingress from private application/data subnets.

## Deployment flow

1. GitHub Actions validates Python, tests, Docker, and Terraform.
2. A versioned backend image is built and pushed to ECR.
3. Terraform provisions or updates AWS infrastructure.
4. An ECS one-off migration task runs `alembic upgrade head`.
5. ECS API and worker services roll out the new image.
6. The ALB routes traffic only to API tasks passing `/ready`.

## Security principles

- no database or Redis public ingress
- least-privilege security-group paths
- secrets injected at runtime from Secrets Manager
- immutable versioned container images
- health-checked deployments
- application and worker logs centralized in CloudWatch

## Cost note

The architecture intentionally models a production-grade AWS deployment. RDS, ElastiCache, ALB, NAT gateways, and continuously running Fargate tasks can incur meaningful charges. Apply the Terraform only when an AWS account and budget/cleanup plan are ready.
