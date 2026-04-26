"""harden pending signup verification flow"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_000002"
down_revision = "20260424_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pending_signups",
        sa.Column("verification_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "pending_signups",
        sa.Column(
            "last_otp_sent_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("pending_signups", "last_otp_sent_at")
    op.drop_column("pending_signups", "verification_attempts")
