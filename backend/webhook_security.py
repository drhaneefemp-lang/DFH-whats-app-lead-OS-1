"""
Webhook Signature Verification for Meta WhatsApp
Uses X-Hub-Signature-256 header to verify webhook authenticity
"""
import hmac
import hashlib
import logging
import os
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# App Secret for signature verification (set in .env)
APP_SECRET = os.environ.get('META_APP_SECRET', '')


def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """
    Verify the webhook signature from Meta
    
    Args:
        payload: Raw request body bytes
        signature_header: X-Hub-Signature-256 header value
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not APP_SECRET:
        logger.warning("META_APP_SECRET not configured - skipping signature verification")
        return True  # Skip verification if secret not configured
    
    if not signature_header:
        logger.warning("No X-Hub-Signature-256 header present")
        return False
    
    # Header format: "sha256=<hash>"
    if not signature_header.startswith('sha256='):
        logger.warning("Invalid signature format")
        return False
    
    expected_signature = signature_header[7:]  # Remove 'sha256=' prefix
    
    # Calculate HMAC-SHA256
    calculated_signature = hmac.new(
        APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(calculated_signature, expected_signature)
    
    if not is_valid:
        logger.warning(f"Signature mismatch: expected {expected_signature[:20]}..., got {calculated_signature[:20]}...")
    
    return is_valid


async def validate_webhook_request(request: Request) -> bytes:
    """
    Validate webhook request and return body if valid
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Raw request body bytes
    
    Raises:
        HTTPException if signature is invalid
    """
    # Get raw body
    body = await request.body()
    
    # Get signature header
    signature_header = request.headers.get('X-Hub-Signature-256', '')
    
    # Verify signature
    if not verify_webhook_signature(body, signature_header):
        logger.error("Webhook signature verification failed")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return body


def is_signature_verification_enabled() -> bool:
    """Check if signature verification is enabled (APP_SECRET is set)"""
    return bool(APP_SECRET)
