# Security Policy

## Supported version

Security fixes are applied to the current `main` branch. This portfolio project does not currently maintain multiple supported release lines.

## Reporting a vulnerability

Please do not publish exploitable details in a public issue. Report a suspected vulnerability privately to the repository owner through an appropriate private contact channel. Include the affected component, reproduction conditions, expected impact, and any safe proof of concept.

## Security model

AI Operations Agent is designed around several trust boundaries:

- public HTTP traffic terminates at the Application Load Balancer;
- only the API service receives ALB ingress;
- application tasks run in private subnets;
- PostgreSQL and Redis are not publicly exposed;
- database access is restricted to the application security group;
- runtime secrets are injected from AWS Secrets Manager;
- human approval gates protect operations classified as requiring approval;
- audit events record important workflow transitions;
- background processing is idempotency-aware to reduce duplicate side effects;
- GitHub Actions CI blocks known vulnerable Python dependencies and Bandit findings.

## Secrets

Never commit `.env` files, passwords, API tokens, AWS access keys, private keys, or production connection strings. The AWS design uses Secrets Manager for runtime database credentials and GitHub Actions OIDC as the foundation for short-lived AWS authentication.

If a secret is accidentally committed, removing it from the latest commit is not sufficient. Revoke/rotate the credential first, then remove it from repository history as appropriate.

## Dependency security

Python dependencies are checked with `pip-audit`. Application source is scanned with Bandit. Dependabot proposes reviewed updates for Python packages and GitHub Actions.

Security-tool output must be evaluated rather than blindly suppressed. Any accepted exception should document the affected rule/advisory, why it is not exploitable in this context, and when it should be reviewed again.

## AI and tool-execution risks

LLM output is not an authorization decision. Tool execution must remain constrained by deterministic policy and workflow state. Operations that require human approval must not be executed merely because a model recommends them.

Inputs and model-generated structured data should be treated as untrusted. Tool adapters should validate their arguments, minimize side effects, and expose only the capabilities required by the workflow.

## Deployment status

The repository contains production-oriented AWS Infrastructure as Code. It is not evidence by itself that a continuously running production environment exists. Real deployment additionally requires reviewed AWS provisioning, TLS/domain configuration, runtime monitoring, backup/restore validation, budget controls, and smoke testing.
