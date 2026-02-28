"""add device_id to votes and user_or_device constraints

Revision ID: a1b2c3d4e5f6
Revises: 250badcd0bb8
Create Date: 2025-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "250badcd0bb8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add device_id column (TEXT, FK to devices.id, nullable)
    op.add_column("votes", sa.Column("device_id", sa.Text(), nullable=True))
    op.create_foreign_key(
        "votes_device_id_fkey",
        "votes",
        "devices",
        ["device_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Make user_id nullable
    op.alter_column(
        "votes",
        "user_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )

    # Drop old unique constraint (one vote per quote per user)
    op.drop_constraint("votes_unique_user", "votes", type_="unique")

    # Add check: exactly one of user_id or device_id must be set
    op.create_check_constraint(
        "votes_user_or_device",
        "votes",
        "(user_id IS NOT NULL) <> (device_id IS NOT NULL)",
    )

    # Partial unique indexes: one vote per (quote_id, user_id) when user_id set, idem for device_id
    op.create_index(
        "votes_unique_user",
        "votes",
        ["quote_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "votes_unique_device",
        "votes",
        ["quote_id", "device_id"],
        unique=True,
        postgresql_where=sa.text("device_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("votes_unique_device", table_name="votes")
    op.drop_index("votes_unique_user", table_name="votes")
    op.drop_constraint("votes_user_or_device", "votes", type_="check")
    op.create_unique_constraint("votes_unique_user", "votes", ["quote_id", "user_id"])
    op.alter_column(
        "votes",
        "user_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )
    op.drop_constraint("votes_device_id_fkey", "votes", type_="foreignkey")
    op.drop_column("votes", "device_id")
