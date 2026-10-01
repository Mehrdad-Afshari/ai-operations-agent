# AI Operations Agent

Production-oriented agentic workflow platform for automating internal service requests with **structured AI decisions, explicit tool calling, human approval, auditability, asynchronous execution, and cloud-ready infrastructure**.

Unlike a chatbot or RAG demo, this project focuses on the engineering problems that appear when an AI system is allowed to propose and execute business actions: authorization boundaries, deterministic policy enforcement, retries, idempotency, approval workflows, audit trails, security gates, observability, and deployment architecture.

> **Deployment status:** the application runs locally with Docker Compose. The repository includes validated, production-oriented AWS Infrastructure as Code, but the AWS environment is intentionally not claimed as a live production deployment until it has been provisioned and operationally verified.

## What it demonstrates

- Agentic workflow orchestration with LangGraph
- Schema-validated structured AI output with Pydantic
- Allow-listed tool calling instead of arbitrary model execution
- Deterministic policy checks outside the LLM
- Human-in-the-loop approval and rejection flows
- PostgreSQL persistence with SQLAlchemy and Alembic migrations
- Celery + Redis asynchronous/background processing
- Idempotency guards and bounded retry/backoff behavior
- Structured JSON logging and correlation IDs
- Separate liveness and database-readiness endpoints
- Docker/Compose containerization and container CI
- AWS ECS/Fargate, ALB, RDS, ElastiCache, ECR, Secrets Manager and CloudWatch modeled with Terraform
- Security quality gates with Bandit and pip-audit
- Ruff, strict mypy, pytest, Docker build and Terraform validation in GitHub Actions
- Dependabot-driven dependency maintenance

## Business workflow

1. A client submits an internal operations request to FastAPI.
2. The request and initial audit event are persisted in PostgreSQL.
3. Celery dispatches processing asynchronously through Redis.
4. The agent produces a schema-validated proposal.
5. Deterministic policy logic evaluates whether the proposed action may execute automatically or requires human approval.
6. Approval/rejection is persisted and audited when human review is required.
7. Approved actions execute only through an explicit tool registry.
8. Terminal state and execution events are persisted for traceability.

The LLM is not the authorization layer. Model output is treated as untrusted input until it passes application-controlled schemas and policy checks.

## Architecture

```text
                         ┌──────────────────────┐
Client ────────────────► │ FastAPI API          │
                         │ /health  /ready      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ PostgreSQL           │
                         │ requests / approvals │
                         │ audit events         │
                         └──────────────────────┘
                                    ▲
                                    │
FastAPI ─► Redis/Celery ─► Worker ─► LangGraph workflow
                                    │
                                    ├─ structured proposal
                                    ├─ deterministic policy
                                    ├─ human approval gate
                                    └─ allow-listed tools
```

The AWS IaC maps the same runtime boundaries to an Application Load Balancer, independent ECS/Fargate API and worker services, private RDS PostgreSQL, private ElastiCache Redis, ECR, Secrets Manager, and CloudWatch.

## Technology stack

### Application
- Python 3.12
- FastAPI
- LangGraph
- Pydantic / pydantic-settings
- SQLAlchemy + Alembic
- PostgreSQL
- Celery + Redis

### Platform and cloud
- Docker + Docker Compose
- Terraform
- AWS ECS/Fargate
- Application Load Balancer
- Amazon RDS for PostgreSQL
- Amazon ElastiCache for Redis
- Amazon ECR
- AWS Secrets Manager
- Amazon CloudWatch
- GitHub Actions OIDC foundation

### Quality and security
- pytest
- Ruff
- mypy
- Bandit
- pip-audit
- Dependabot
- GitHub Actions

## Local development

### Prerequisites

- Docker with Docker Compose support

### Start the stack

```bash
cp .env.example .env
docker compose up --build
```

The Compose stack starts PostgreSQL, Redis, applies Alembic migrations, and runs the API and worker services.

Check the API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Stop the stack:

```bash
docker compose down
```

To remove local persisted data as well:

```bash
docker compose down -v
```

## Quality gates

Pull requests are validated by independent GitHub Actions jobs:

```text
Backend     Ruff → mypy → pytest
Security    pip-audit → Bandit
Containers  docker compose config → docker build
Terraform   terraform fmt → terraform init -backend=false → terraform validate
```

A known-vulnerability finding is treated as a CI failure rather than a decorative report. During development, this gate identified vulnerable dependency versions; the dependencies were upgraded and compatibility issues were fixed before the milestone was considered complete.

## Reliability and observability

Celery has at-least-once delivery semantics, so background processing is designed to avoid repeating terminal or approval-waiting work during retry/redelivery. Transient failures use bounded exponential backoff.

HTTP requests propagate or receive an `X-Correlation-ID`. Application logs use structured JSON so request failures can be correlated across operational investigation. `/health` reports process liveness while `/ready` verifies database readiness and is used by the AWS load-balancer health model.

## AWS Infrastructure as Code

`infra/aws/` contains the Terraform deployment architecture, including:

- two-AZ VPC structure with public/private network tiers
- internet-facing ALB with `/ready` target health checks
- independent Fargate API and worker services
- private encrypted RDS PostgreSQL
- private encrypted ElastiCache Redis
- immutable, scan-on-push ECR repository
- Secrets Manager-backed runtime database credentials
- CloudWatch log groups and ECS Container Insights
- one-off Fargate task definition for `alembic upgrade head`
- GitHub Actions OIDC trust foundation scoped to this repository

The Terraform stack is validated in CI but is **not automatically applied**. Provisioning these resources can create AWS charges and therefore requires an explicit account, budget, deployment-permission and teardown decision.

See [`infra/aws/README.md`](infra/aws/README.md) for the cloud architecture and [`docs/PRODUCTION.md`](docs/PRODUCTION.md) for deployment/rollback operations.

## Security model

Important boundaries include:

- the LLM does not authorize actions;
- model output is schema validated;
- executable capabilities are allow-listed;
- approval decisions are persisted and auditable;
- RDS and Redis are private in the AWS design;
- runtime database credentials are modeled through Secrets Manager;
- long-lived AWS access keys are avoided in favor of an OIDC trust foundation;
- dependency and source-code security checks block CI on findings.

See [`SECURITY.md`](SECURITY.md) for the detailed security policy and threat boundaries.

## Repository structure

```text
.
├── backend/
│   ├── alembic/             # database migrations
│   ├── app/                 # API, workflow, policy, tools, persistence, worker
│   ├── tests/               # backend and reliability tests
│   ├── Dockerfile
│   └── requirements*.txt
├── docs/
│   └── PRODUCTION.md        # operations, rollback, incident and recovery runbook
├── infra/aws/               # Terraform AWS architecture
├── .github/
│   ├── workflows/ci.yml     # backend/security/container/Terraform quality gates
│   └── dependabot.yml
├── docker-compose.yml
├── SECURITY.md
└── README.md
```

## Production-readiness boundary

This repository demonstrates production-oriented engineering practices. A claim of an actually running production AWS service would additionally require evidence from a provisioned environment: successful image push and migration, ECS rollout, TLS/domain configuration, runtime monitoring, backup/restore testing, budget controls, and an end-to-end smoke test.

That distinction is deliberate: infrastructure code and architecture are evidence of engineering capability, but they are not presented as operational evidence that has not yet been produced.

## Portfolio relevance

This project is intended to provide concrete evidence for roles such as **Applied AI Engineer, AI Developer, AI Solutions Developer, Python/Backend Developer, and Software Developer with an AI focus**.

Recruiter/ATS-relevant technologies demonstrated by the repository include: **Python, FastAPI, LangGraph, agentic workflows, tool calling, structured outputs, human-in-the-loop, PostgreSQL, SQLAlchemy, Alembic, Redis, Celery, asynchronous processing, Docker, Docker Compose, Terraform, AWS ECS/Fargate, RDS, ElastiCache, ECR, Secrets Manager, CloudWatch, CI/CD, GitHub Actions, security scanning, observability, idempotency, retry/backoff, testing, Ruff, mypy, pytest, Bandit, pip-audit, and Infrastructure as Code**.
