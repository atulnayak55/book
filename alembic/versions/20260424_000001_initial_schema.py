"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260424_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(op.f("ix_departments_name"), "departments", ["name"], unique=True)

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_subjects_id"), "subjects", ["id"], unique=False)
    op.create_index(op.f("ix_subjects_name"), "subjects", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("unipd_id", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=False)
    op.create_index(op.f("ix_users_unipd_id"), "users", ["unipd_id"], unique=True)

    op.create_table(
        "pending_signups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("unipd_id", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("otp_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(op.f("ix_pending_signups_email"), "pending_signups", ["email"], unique=True)
    op.create_index(op.f("ix_pending_signups_id"), "pending_signups", ["id"], unique=False)

    op.create_table(
        "programs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index(op.f("ix_programs_id"), "programs", ["id"], unique=False)
    op.create_index(op.f("ix_programs_name"), "programs", ["name"], unique=False)

    op.create_table(
        "program_subjects",
        sa.Column("program_id", sa.Integer(), sa.ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("condition", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_listings_id"), "listings", ["id"], unique=False)
    op.create_index(op.f("ix_listings_title"), "listings", ["title"], unique=False)

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(op.f("ix_auth_tokens_id"), "auth_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_auth_tokens_purpose"), "auth_tokens", ["purpose"], unique=False)
    op.create_index(op.f("ix_auth_tokens_token_hash"), "auth_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_auth_tokens_user_id"), "auth_tokens", ["user_id"], unique=False)

    op.create_table(
        "chat_rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=True),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index(op.f("ix_chat_rooms_id"), "chat_rooms", ["id"], unique=False)

    op.create_table(
        "listing_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index(op.f("ix_listing_images_id"), "listing_images", ["id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_listing_images_id"), table_name="listing_images")
    op.drop_table("listing_images")
    op.drop_index(op.f("ix_chat_rooms_id"), table_name="chat_rooms")
    op.drop_table("chat_rooms")
    op.drop_index(op.f("ix_auth_tokens_user_id"), table_name="auth_tokens")
    op.drop_index(op.f("ix_auth_tokens_token_hash"), table_name="auth_tokens")
    op.drop_index(op.f("ix_auth_tokens_purpose"), table_name="auth_tokens")
    op.drop_index(op.f("ix_auth_tokens_id"), table_name="auth_tokens")
    op.drop_table("auth_tokens")
    op.drop_index(op.f("ix_listings_title"), table_name="listings")
    op.drop_index(op.f("ix_listings_id"), table_name="listings")
    op.drop_table("listings")
    op.drop_table("program_subjects")
    op.drop_index(op.f("ix_programs_name"), table_name="programs")
    op.drop_index(op.f("ix_programs_id"), table_name="programs")
    op.drop_table("programs")
    op.drop_index(op.f("ix_pending_signups_id"), table_name="pending_signups")
    op.drop_index(op.f("ix_pending_signups_email"), table_name="pending_signups")
    op.drop_table("pending_signups")
    op.drop_index(op.f("ix_users_unipd_id"), table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_subjects_name"), table_name="subjects")
    op.drop_index(op.f("ix_subjects_id"), table_name="subjects")
    op.drop_table("subjects")
    op.drop_index(op.f("ix_departments_name"), table_name="departments")
    op.drop_index(op.f("ix_departments_id"), table_name="departments")
    op.drop_table("departments")
