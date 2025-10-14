"""add_ingredient_images_table

Revision ID: 08272dd0516b
Revises: b8753f97e123
Create Date: 2025-10-13 06:01:16.690697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08272dd0516b'
down_revision: Union[str, None] = 'b8753f97e123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ingredient_images',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('photographer', sa.String(255), nullable=True),
        sa.Column('photographer_url', sa.Text(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('alt_text', sa.Text(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False, server_default='false'),
        sa.Column('is_approved', sa.Boolean(), default=True, server_default='true'),
        sa.Column('display_order', sa.Integer(), default=0, server_default='0'),
        sa.Column('relevance_score', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_ingredient_images_ingredient_id', 'ingredient_images', ['ingredient_id'])
    op.create_index('ix_ingredient_images_is_primary', 'ingredient_images', ['is_primary'])


def downgrade() -> None:
    op.drop_index('ix_ingredient_images_is_primary')
    op.drop_index('ix_ingredient_images_ingredient_id')
    op.drop_table('ingredient_images')
