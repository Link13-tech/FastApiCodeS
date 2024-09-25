"""Fix UUID generation

Revision ID: 186251c6719c
Revises: ac4dec5c7907
Create Date: 2024-09-23 20:11:14.902710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '186251c6719c'
down_revision: Union[str, None] = 'ac4dec5c7907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем тип столбца uuid с использованием USING
    op.alter_column('snippets', 'uuid',
                    existing_type=sa.String(),
                    type_=sa.UUID(),
                    postgresql_using='uuid::uuid')
    op.create_unique_constraint(None, 'snippets', ['uuid'])


def downgrade() -> None:
    op.drop_constraint(None, 'snippets', type_='unique')
    op.alter_column('snippets', 'uuid',
                    existing_type=sa.UUID(),
                    type_=sa.String())
