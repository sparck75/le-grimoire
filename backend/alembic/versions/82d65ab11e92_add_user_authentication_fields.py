"""add_user_authentication_fields

Revision ID: 82d65ab11e92
Revises: 51d56accfc10
Create Date: 2025-10-26 22:06:00.436265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82d65ab11e92'
down_revision: Union[str, None] = '51d56accfc10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add username column
    op.add_column('users', sa.Column('username', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Add password_hash column
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    
    # Add role column with enum type
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'collaborator', 'reader')")
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'collaborator', 'reader', name='userrole'), nullable=True))
    
    # Add is_active column
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # Make oauth fields nullable
    op.alter_column('users', 'oauth_provider', nullable=True)
    op.alter_column('users', 'oauth_provider_id', nullable=True)
    
    # Set default values for existing rows
    op.execute("UPDATE users SET role = 'reader' WHERE role IS NULL")
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET username = SPLIT_PART(email, '@', 1) WHERE username IS NULL")
    
    # Make new columns non-nullable
    op.alter_column('users', 'role', nullable=False)
    op.alter_column('users', 'is_active', nullable=False)
    op.alter_column('users', 'username', nullable=False)


def downgrade() -> None:
    # Remove new columns
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.execute('DROP TYPE userrole')
    
    # Restore oauth fields to non-nullable
    op.alter_column('users', 'oauth_provider', nullable=False)
    op.alter_column('users', 'oauth_provider_id', nullable=False)
