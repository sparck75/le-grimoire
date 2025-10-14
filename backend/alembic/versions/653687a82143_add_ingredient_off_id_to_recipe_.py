"""add_ingredient_off_id_to_recipe_ingredients

Revision ID: 653687a82143
Revises: 08272dd0516b
Create Date: 2025-10-13 16:28:26.192055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653687a82143'
down_revision: Union[str, None] = '08272dd0516b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new ingredient_off_id column
    op.add_column('recipe_ingredients', sa.Column('ingredient_off_id', sa.String(length=255), nullable=True))
    
    # Make old ingredient_id nullable for backward compatibility
    op.alter_column('recipe_ingredients', 'ingredient_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    
    # Note: Data migration would go here if needed
    # For now, new recipes will use ingredient_off_id, old ones can keep ingredient_id


def downgrade() -> None:
    # Remove the new column
    op.drop_column('recipe_ingredients', 'ingredient_off_id')
    
    # Restore ingredient_id to NOT NULL
    op.alter_column('recipe_ingredients', 'ingredient_id',
               existing_type=sa.INTEGER(),
               nullable=False)
