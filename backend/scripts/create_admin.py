"""
Create initial admin user
"""
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
import sys


def create_admin_user():
    """Create an admin user for initial setup"""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_email = "admin@legrimoire.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            print(f"Role: {existing_admin.role.value}")
            return
        
        # Create admin user
        admin_password = "admin123"
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            username="admin",
            password_hash=hashed_password,
            role="admin",
            is_active=True,
            name="Administrator"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("=" * 60)
        print("Admin user created successfully!")
        print("=" * 60)
        print(f"Email: {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print(f"Password: {admin_password}")
        print(f"Role: {admin_user.role}")
        print("=" * 60)
        print("⚠️  IMPORTANT: Change the admin password after first login!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
