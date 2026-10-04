"""add_todos_user_completed_created_index

Revision ID: c4d2a7f1b9e3
Revises: 3b0a5f793ae1
Create Date: 2026-10-04 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c4d2a7f1b9e3'
down_revision: Union[str, None] = '3b0a5f793ae1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Serves "todos of a user" (filter, count, ORDER BY created_at).
    op.create_index(
        "ix_todos_user_id_completed_created_at",
        "todos",
        ["user_id", "completed", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_todos_user_id_completed_created_at", table_name="todos")
