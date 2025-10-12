"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()

class OAuthLoginRequest(BaseModel):
    """OAuth login request"""
    provider: str  # 'google' or 'apple'
    provider_id: str
    email: str
    name: str = None
    avatar_url: str = None

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/oauth/login", response_model=TokenResponse)
async def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """
    OAuth login endpoint for Google and Apple
    Creates or updates user and returns access token
    """
    # Check if user exists
    user = db.query(User).filter(
        User.oauth_provider == request.provider,
        User.oauth_provider_id == request.provider_id
    ).first()
    
    if not user:
        # Create new user
        user = User(
            email=request.email,
            name=request.name,
            avatar_url=request.avatar_url,
            oauth_provider=request.provider,
            oauth_provider_id=request.provider_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user information
        if request.name:
            user.name = request.name
        if request.avatar_url:
            user.avatar_url = request.avatar_url
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url
        }
    }

@router.get("/me")
async def get_current_user():
    """Get current authenticated user"""
    # This would normally use a dependency to extract the user from the JWT token
    # For now, return a placeholder
    return {"message": "Current user endpoint - requires authentication middleware"}
