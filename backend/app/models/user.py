"""
User model for authentication and authorization
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    COLLABORATOR = "collaborator"
    READER = "reader"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(
        Enum('admin', 'collaborator', 'reader', name='userrole'),
        default='reader',
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # OAuth fields (optional)
    name = Column(String(255))
    avatar_url = Column(String)
    oauth_provider = Column(String(50))  # 'google', 'apple', or None for password auth
    oauth_provider_id = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.username} ({self.email}) - {self.role}>"
