"""Change uuid column to UUID type

Revision ID: be6a2cdeda91
Revises: b2d75488aca0
Create Date: 2024-09-23 20:18:51.773923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be6a2cdeda91'
down_revision: Union[str, None] = 'b2d75488aca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
