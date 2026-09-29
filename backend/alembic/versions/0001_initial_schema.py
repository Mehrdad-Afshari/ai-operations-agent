"""Create operation requests, approvals, and audit events.

Revision ID: 0001
Revises: None
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

request_status = sa.Enum(
    "RECEIVED",
    "PROCESSING",
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "COMPLETED",
    "FAILED",
    name="requeststatus",
)
risk_level = sa.Enum("LOW", "MEDIUM", "HIGH", name="risklevel")
approval_outcome = sa.Enum("APPROVED", "REJECTED", name="approvaloutcome")


def upgrade() -> None:
    op.create_table(
        "operation_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requester", sa.String(length=200), nullable=False),
        sa.Column("status", request_status, nullable=False),
        sa.Column("risk_level", risk_level, nullable=True),
        sa.Column("proposed_tool", sa.String(length=100), nullable=True),
        sa.Column("proposed_arguments", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operation_requests_status", "operation_requests", ["status"])

    op.create_table(
        "approval_decisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("outcome", approval_outcome, nullable=False),
        sa.Column("actor", sa.String(length=200), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["operation_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id", name="uq_approval_request_id"),
    )
    op.create_index("ix_approval_decisions_request_id", "approval_decisions", ["request_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("actor", sa.String(length=200), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["operation_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_request_id", "audit_events", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_request_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_approval_decisions_request_id", table_name="approval_decisions")
    op.drop_table("approval_decisions")
    op.drop_index("ix_operation_requests_status", table_name="operation_requests")
    op.drop_table("operation_requests")
    approval_outcome.drop(op.get_bind(), checkfirst=True)
    risk_level.drop(op.get_bind(), checkfirst=True)
    request_status.drop(op.get_bind(), checkfirst=True)
