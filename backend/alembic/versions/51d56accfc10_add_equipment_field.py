"""add_equipment_field

Revision ID: 51d56accfc10
Revises: 78827b0e0d34
Create Date: 2025-10-26 21:08:19.750323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51d56accfc10'
down_revision: Union[str, None] = '78827b0e0d34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add equipment column to recipes table
    op.add_column('recipes', sa.Column('equipment', sa.ARRAY(sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove equipment column from recipes table
    op.drop_column('recipes', 'equipment')
