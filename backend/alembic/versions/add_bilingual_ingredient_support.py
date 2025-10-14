"""add_bilingual_ingredient_support

Revision ID: b8753f97e123
Revises: 7a642e86d852
Create Date: 2025-10-13 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8753f97e123'
down_revision: Union[str, None] = '7a642e86d852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop and recreate ingredients table with integer ID and bilingual support
    op.execute('DROP TABLE IF EXISTS recipe_ingredients CASCADE')
    op.execute('DROP TABLE IF EXISTS ingredients CASCADE')
    
    # Create new ingredients table with integer ID
    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('english_name', sa.String(255), nullable=False),
        sa.Column('french_name', sa.String(255), nullable=False),
        sa.Column('gender', sa.String(1), nullable=True),
        sa.Column('name_plural', sa.String(255), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredient_categories.id'), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('default_unit', sa.String(50), nullable=True),
        sa.Column('aliases', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Recreate recipe_ingredients table with integer foreign key
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ingredient_id', sa.Integer, sa.ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 3), nullable=True),
        sa.Column('quantity_max', sa.Numeric(10, 3), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('preparation_notes', sa.Text, nullable=True),
        sa.Column('is_optional', sa.Boolean, server_default='false'),
        sa.Column('display_order', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Add bilingual columns to ingredient_categories
    op.add_column('ingredient_categories', sa.Column('name_en', sa.String(100), nullable=True))
    op.add_column('ingredient_categories', sa.Column('name_fr', sa.String(100), nullable=True))


def downgrade() -> None:
    # Remove bilingual columns from ingredient_categories
    op.drop_column('ingredient_categories', 'name_fr')
    op.drop_column('ingredient_categories', 'name_en')
    
    # Drop and recreate tables with UUID IDs (original schema)
    op.execute('DROP TABLE IF EXISTS recipe_ingredients CASCADE')
    op.execute('DROP TABLE IF EXISTS ingredients CASCADE')
    
    op.create_table(
        'ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('name_plural', sa.String(255), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredient_categories.id'), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('default_unit', sa.String(50), nullable=True),
        sa.Column('aliases', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 3), nullable=True),
        sa.Column('quantity_max', sa.Numeric(10, 3), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('preparation_notes', sa.Text, nullable=True),
        sa.Column('is_optional', sa.Boolean, server_default='false'),
        sa.Column('display_order', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
