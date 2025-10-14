"""add_ingredient_off_id_to_shopping_list_items

Revision ID: 210983c36263
Revises: 653687a82143
Create Date: 2025-10-13 16:36:52.331470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '210983c36263'
down_revision: Union[str, None] = '653687a82143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ingredient_off_id column to shopping_list_items
    op.add_column('shopping_list_items', sa.Column('ingredient_off_id', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove ingredient_off_id column from shopping_list_items
    op.drop_column('shopping_list_items', 'ingredient_off_id')
