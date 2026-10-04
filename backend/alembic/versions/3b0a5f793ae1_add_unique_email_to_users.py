"""add_unique_email_to_users

Revision ID: 3b0a5f793ae1
Revises: a0790c76a129
Create Date: 2026-10-04 15:03:02.132042

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3b0a5f793ae1'
down_revision: Union[str, None] = 'a0790c76a129'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fails if duplicate emails already exist; remove them before upgrading.
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
