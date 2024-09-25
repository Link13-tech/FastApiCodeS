"""бъединение миграций

Revision ID: e1225154d16e
Revises: 186251c6719c, be6a2cdeda91
Create Date: 2024-09-23 20:27:44.932159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1225154d16e'
down_revision: Union[str, None] = ('186251c6719c', 'be6a2cdeda91')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
