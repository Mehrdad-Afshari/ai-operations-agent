# AI Operations Agent

Production-oriented agentic workflow platform for automating internal service requests with structured AI decisions, tool calling, human approval, auditability, and asynchronous execution.

## Project goal

This project models a real business workflow rather than another chatbot/RAG demo:

1. A user submits an internal operations request.
2. The API persists it in PostgreSQL.
3. A background worker processes it asynchronously.
4. An agent produces schema-validated structured output.
5. Policy rules decide whether the proposed action can run automatically or requires human approval.
6. Approved actions run through an explicit allow-listed tool registry.
7. Workflow transitions and tool executions are auditable.

## Target stack

- Next.js + TypeScript + Tailwind CSS
- FastAPI + Python 3.12
- PostgreSQL + SQLAlchemy + Alembic
- Redis + Celery
- LangGraph
- Pydantic structured outputs
- Docker / Docker Compose
- AWS ECS Fargate, RDS, CloudWatch
- Terraform
- GitHub Actions
- OpenTelemetry
- pytest, Ruff, mypy

## Status

Milestone 1 — Foundation in progress.
