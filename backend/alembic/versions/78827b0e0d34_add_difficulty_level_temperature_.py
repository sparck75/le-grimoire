"""Add difficulty_level, temperature, temperature_unit, and notes to recipes

Revision ID: 78827b0e0d34
Revises: 210983c36263
Create Date: 2025-10-13 19:35:57.696016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78827b0e0d34'
down_revision: Union[str, None] = '210983c36263'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to recipes table
    op.add_column('recipes', sa.Column('difficulty_level', sa.String(length=50), nullable=True))
    op.add_column('recipes', sa.Column('temperature', sa.Integer(), nullable=True))
    op.add_column('recipes', sa.Column('temperature_unit', sa.String(length=10), nullable=True))
    op.add_column('recipes', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('recipes', 'notes')
    op.drop_column('recipes', 'temperature_unit')
    op.drop_column('recipes', 'temperature')
    op.drop_column('recipes', 'difficulty_level')
