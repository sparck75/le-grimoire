"""add_ingredient_system

Revision ID: 7a642e86d852
Revises: 
Create Date: 2025-10-13 00:39:11.567902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a642e86d852'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ingredient_categories table
    op.create_table(
        'ingredient_categories',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('parent_category_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredient_categories.id'), nullable=True),
        sa.Column('display_order', sa.Integer, nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create units table
    op.create_table(
        'units',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('abbreviation', sa.String(20), nullable=True),
        sa.Column('type', sa.String(50), nullable=True),  # 'volume', 'weight', 'unit', 'temperature'
        sa.Column('system', sa.String(20), nullable=True),  # 'metric', 'imperial', 'both'
        sa.Column('conversion_to_base', sa.Numeric(10, 6), nullable=True),
        sa.Column('base_unit', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('name_plural', sa.String(255), nullable=True),
        sa.Column('category_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredient_categories.id'), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('default_unit', sa.String(50), nullable=True),
        sa.Column('aliases', sa.dialects.postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create recipe_ingredients junction table
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('recipe_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ingredient_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 3), nullable=True),
        sa.Column('quantity_max', sa.Numeric(10, 3), nullable=True),  # for ranges
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('preparation_notes', sa.Text, nullable=True),  # "chopped", "diced", etc.
        sa.Column('is_optional', sa.Boolean, default=False, server_default='false'),
        sa.Column('display_order', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Add new columns to recipes table
    op.add_column('recipes', sa.Column('difficulty_level', sa.String(50), nullable=True))
    op.add_column('recipes', sa.Column('temperature', sa.Integer, nullable=True))
    op.add_column('recipes', sa.Column('temperature_unit', sa.String(10), nullable=True))
    op.add_column('recipes', sa.Column('notes', sa.Text, nullable=True))
    
    # Create indexes for better performance
    op.create_index('idx_ingredients_name', 'ingredients', ['name'])
    op.create_index('idx_ingredients_category', 'ingredients', ['category_id'])
    op.create_index('idx_recipe_ingredients_recipe', 'recipe_ingredients', ['recipe_id'])
    op.create_index('idx_recipe_ingredients_ingredient', 'recipe_ingredients', ['ingredient_id'])
    
    # Create trigger for ingredients updated_at
    op.execute("""
        CREATE TRIGGER update_ingredients_updated_at 
        BEFORE UPDATE ON ingredients
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_ingredients_updated_at ON ingredients;")
    
    # Drop indexes
    op.drop_index('idx_recipe_ingredients_ingredient')
    op.drop_index('idx_recipe_ingredients_recipe')
    op.drop_index('idx_ingredients_category')
    op.drop_index('idx_ingredients_name')
    
    # Remove columns from recipes
    op.drop_column('recipes', 'notes')
    op.drop_column('recipes', 'temperature_unit')
    op.drop_column('recipes', 'temperature')
    op.drop_column('recipes', 'difficulty_level')
    
    # Drop tables in reverse order
    op.drop_table('recipe_ingredients')
    op.drop_table('ingredients')
    op.drop_table('units')
    op.drop_table('ingredient_categories')
