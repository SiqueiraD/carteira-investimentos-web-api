"""create account table

Revision ID: 7364089fa2e6
Revises: d87c8de5d447
Create Date: 2024-12-20 04:23:51.678121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7364089fa2e6'
down_revision: Union[str, None] = 'd87c8de5d447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
