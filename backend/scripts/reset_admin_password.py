#!/usr/bin/env python3
"""Reset admin password in PostgreSQL"""
import asyncio
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Database connection
DATABASE_URL = "postgresql://grimoire:grimoire_password@localhost:5432/le_grimoire"

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin_password(email: str, new_password: str):
    """Reset admin user password"""
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Hash password
    password_hash = pwd_context.hash(new_password)
    print(f"Generated hash: {password_hash}")
    
    # Update database
    with engine.connect() as conn:
        result = conn.execute(
            text("UPDATE users SET password_hash = :hash WHERE email = :email"),
            {"hash": password_hash, "email": email}
        )
        conn.commit()
        print(f"Updated {result.rowcount} user(s)")
        
        # Verify
        result = conn.execute(
            text("SELECT email, username, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        if user:
            print(f"User found: {user[0]} ({user[1]}) - Role: {user[2]}")
        else:
            print("User not found!")

if __name__ == "__main__":
    reset_admin_password("admin@legrimoireonline.ca", "admin123")
