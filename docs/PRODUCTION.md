# Production Operations Runbook

This runbook documents the operational model for AI Operations Agent. The repository contains production-oriented AWS infrastructure as code, but the AWS stack is not automatically provisioned.

## Runtime topology

- FastAPI runs as an ECS/Fargate API service behind an Application Load Balancer.
- Celery runs as an independent ECS/Fargate worker service.
- PostgreSQL is provided by private Amazon RDS.
- Redis is provided by private Amazon ElastiCache and is used as the Celery broker/result backend.
- Container images are stored in Amazon ECR.
- Runtime secrets are injected from AWS Secrets Manager.
- API, worker, and migration logs are sent to CloudWatch Logs.
- Database migrations run as a one-off ECS/Fargate task before an application rollout.

## Deployment sequence

1. Require a green CI run: Ruff, mypy, pytest, dependency audit, Bandit, Docker build, Compose validation, Terraform formatting and validation.
2. Build the backend image from the reviewed commit.
3. Tag the image with an immutable identifier such as the Git commit SHA.
4. Push the image to the configured ECR repository.
5. Update the Terraform `image_tag` input to the immutable image identifier and review the Terraform plan.
6. Apply reviewed infrastructure changes.
7. Run the migration task definition and require a successful exit code from `alembic upgrade head`.
8. Roll out the API and worker ECS services.
9. Wait for the ALB target group to report the API healthy through `/ready`.
10. Verify a representative operation request, approval path, worker execution, audit events, and structured logs.

Do not deploy an unreviewed mutable image tag such as `latest`.

## Health model

`GET /health` is a liveness signal: the process is running.

`GET /ready` is a readiness signal: the application can reach its database. The ALB uses readiness rather than liveness so traffic is not routed to an API task that cannot serve database-backed requests.

## Migration failure

If the migration task fails:

1. Do not roll out the new API or worker task definition.
2. Inspect the migration CloudWatch log stream.
3. Identify whether the failure is schema, connectivity, credentials, or image related.
4. Fix the migration in a reviewed pull request.
5. Rebuild an immutable image and rerun the migration.

Never bypass a failed migration by manually editing the production schema.

## Application rollout failure

If new API tasks do not become healthy:

1. Keep or restore the last known-good task definition/image.
2. Inspect ALB target health and API CloudWatch logs.
3. Check `/ready`, database connectivity, secret injection, and container startup errors.
4. Roll the ECS service back to the last known-good task definition if the issue is release-specific.

If worker tasks fail while API tasks remain healthy, stop the worker rollout independently and inspect the worker logs and Redis connectivity. API and worker services are deliberately separate failure domains.

## Background-job reliability

Celery has at-least-once delivery semantics. Operation processing therefore contains idempotency guards so terminal or approval-waiting requests are not processed twice during retry/redelivery. Retries are bounded and use exponential backoff for transient connection/time-out failures.

When investigating a suspected duplicate execution, correlate request state, audit events, worker logs, and the operation request identifier before retrying manually.

## Observability

HTTP requests receive an `X-Correlation-ID`. If a caller supplies one, it is propagated; otherwise the API generates one. Application logs are structured JSON and include the correlation ID.

For an incident, start with:

1. request/correlation ID;
2. API CloudWatch log stream;
3. worker CloudWatch log stream;
4. operation request state and audit events;
5. RDS/Redis connectivity and ECS task health.

## Security operations

- Do not commit credentials, database passwords, AWS keys, or `.env` files.
- Prefer GitHub Actions OIDC over long-lived AWS access keys.
- Keep RDS and Redis private; they must not accept public ingress.
- Runtime database credentials belong in Secrets Manager.
- Review Dependabot pull requests rather than automatically merging dependency changes.
- `pip-audit` and Bandit are blocking CI quality gates.
- Treat a security-gate failure as a release blocker unless a documented, reviewed exception exists.

## Backup and data recovery

RDS automated backups are configured in Terraform. Before a real production launch, define and test the required recovery-point objective (RPO) and recovery-time objective (RTO), snapshot retention, and a restore drill. A backup configuration is not considered a recovery strategy until restoration has been tested.

## Cost and teardown

The AWS architecture includes billable services such as Fargate, RDS, ElastiCache, and an ALB. Before `terraform apply`:

- configure an AWS Budget and billing alerts;
- review the Terraform plan and expected monthly cost;
- decide whether deletion protection should be enabled;
- document which data must be retained before teardown.

For a temporary portfolio deployment, preserve any required data/snapshots first, then destroy the Terraform-managed environment when the demonstration period ends.

## Production readiness boundary

The repository demonstrates production-oriented engineering practices, but a real production claim requires evidence from an actually provisioned environment: successful migration and rollout, TLS/domain configuration, runtime monitoring, backup/restore testing, budget controls, and an operational smoke test. Until those steps are completed, describe the AWS stack as **production-oriented infrastructure as code**, not as a continuously running production service.
