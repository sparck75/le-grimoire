"""
Admin user management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_active_admin, get_password_hash
from app.models.user import User, UserRole

router = APIRouter()


class UserListResponse(BaseModel):
    """User list response"""
    id: str
    email: str
    username: str
    role: str
    is_active: bool
    name: Optional[str] = None
    oauth_provider: Optional[str] = None
    created_at: str


class UserDetailResponse(BaseModel):
    """User detail response"""
    id: str
    email: str
    username: str
    role: str
    is_active: bool
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_provider_id: Optional[str] = None
    created_at: str
    updated_at: str


class UserUpdateRequest(BaseModel):
    """User update request"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleUpdateRequest(BaseModel):
    """User role update request"""
    role: str


class UserCreateRequest(BaseModel):
    """Admin user creation request"""
    email: EmailStr
    username: str
    password: Optional[str] = None
    role: str = "reader"
    is_active: bool = True


@router.get("/", response_model=List[UserListResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)
    """
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        UserListResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            name=user.name,
            oauth_provider=user.oauth_provider,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get user details (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        name=user.name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.post("/", response_model=UserDetailResponse)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()
    
    if existing_user:
        if existing_user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Validate role
    try:
        user_role = UserRole(request.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
        )
    
    # Create user
    password_hash = get_password_hash(request.password) if request.password else None
    user = User(
        email=request.email,
        username=request.username,
        password_hash=password_hash,
        role=user_role,
        is_active=request.is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        name=user.name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Update user details (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if request.email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(
            User.email == request.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = request.email
    
    if request.username is not None:
        # Check if username is already taken
        existing = db.query(User).filter(
            User.username == request.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = request.username
    
    if request.name is not None:
        user.name = request.name
    
    if request.is_active is not None:
        user.is_active = request.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        name=user.name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role(
    user_id: UUID,
    request: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role
    try:
        user_role = UserRole(request.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
        )
    
    user.role = user_role
    db.commit()
    db.refresh(user)
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        name=user.name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
