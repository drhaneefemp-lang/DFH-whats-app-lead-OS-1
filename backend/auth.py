"""
API Key authentication for WhatsApp Business API service
"""
import secrets
import hashlib
import logging
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"wa_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Hash API key for secure storage"""
    return hashlib.sha256(key.encode()).hexdigest()


async def validate_api_key(
    api_key: Optional[str],
    db: AsyncIOMotorDatabase
) -> bool:
    """
    Validate API key against database
    
    Args:
        api_key: The API key from request header
        db: Database instance
    
    Returns:
        True if valid, raises HTTPException otherwise
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    # Hash the provided key and look it up
    key_hash = hash_api_key(api_key)
    
    api_key_doc = await db.api_keys.find_one(
        {"key": key_hash, "is_active": True},
        {"_id": 0}
    )
    
    if not api_key_doc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key"
        )
    
    # Update last used timestamp
    await db.api_keys.update_one(
        {"key": key_hash},
        {"$set": {"last_used_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return True


def get_api_key_dependency(db: AsyncIOMotorDatabase):
    """
    Create API key validation dependency for routes
    
    Args:
        db: Database instance
    
    Returns:
        Dependency function
    """
    async def verify_api_key(api_key: str = Security(api_key_header)):
        await validate_api_key(api_key, db)
        return api_key
    
    return verify_api_key
