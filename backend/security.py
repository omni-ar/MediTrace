"""
Phase 5: Security Foundation
=============================
JWT Authentication + RBAC + Redis Rate Limiting

Architectural Notes:
- The JWT payload contains ONLY `sub` (user_id) and `exp`. 
  The role is NOT embedded in the token to prevent the Stale Claims 
  Vulnerability. Every request performs a live database lookup to 
  retrieve the user's current role and is_active status.
- For a production system at high TPS, the live check should be 
  replaced with a Redis-cached user session to avoid per-request 
  disk reads. For this SQLite prototype, the DB read is acceptable.
- datetime.now(timezone.utc) is used instead of the deprecated 
  datetime.utcnow() to prevent timezone validation failures.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import get_db

# ============================================================
# CONFIGURATION
# ============================================================

SECRET_KEY = "meditrace-jwt-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting: max requests per window per IP for /verify-image
RATE_LIMIT_MAX_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

# ============================================================
# PASSWORD CRYPTOGRAPHY (bcrypt)
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plaintext password against bcrypt hash.
    passlib handles salt extraction and constant-time comparison internally."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash with automatic salt generation.
    Cost factor defaults to 12 rounds (2^12 iterations)."""
    return pwd_context.hash(password)


# ============================================================
# JWT TOKEN GENERATION
# ============================================================

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT containing ONLY the subject identifier.
    
    The role is deliberately excluded from the payload to prevent 
    the Stale Claims Vulnerability: if an admin revokes a user's 
    privileges, the change takes effect immediately on the next 
    request because the role is fetched live from the database, 
    not from a cached token claim.
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================
# AUTHENTICATION DEPENDENCY (Live DB Check)
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Core authentication dependency. Decodes the JWT, then performs 
    a LIVE database lookup to verify the user exists and is active.
    
    This eliminates the Stale Claims Vulnerability: even if a token 
    is mathematically valid, a revoked or deactivated user is 
    rejected instantly.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    # --- LIVE CHECK ---
    # This is the critical difference from a pure stateless system.
    # We hit the database on every request to get the REAL, CURRENT
    # user state. The JWT is merely a signed session identifier.
    user = db.query(models.User).filter(models.User.id == int(user_id_str)).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated. Contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ============================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================

class RequireRole:
    """
    Reusable FastAPI dependency that enforces role-based access.

    Usage in endpoint signature:
        user: models.User = Depends(RequireRole(["manufacturer", "admin"]))

    Execution order:
        1. OAuth2PasswordBearer extracts the Bearer token from the header.
        2. get_current_user decodes the JWT, queries the DB, and verifies 
           the user is active.
        3. RequireRole checks if the user's live role is in the allowed list.
        4. If not, raises HTTP 403 Forbidden BEFORE the endpoint body executes.
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{current_user.role}' does not have access. "
                       f"Required: {self.allowed_roles}",
            )
        return current_user


# ============================================================
# RATE LIMITER (Redis-backed, IP-based)
# ============================================================

import redis

_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    """Lazy-initialize a Redis connection for rate limiting.
    Falls back gracefully if Redis is unavailable (dev mode)."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
            _redis_client.ping()
        except redis.ConnectionError:
            print("[SECURITY] Redis unavailable for rate limiting. Falling back to unrestricted mode.")
            _redis_client = None
    return _redis_client


def rate_limit_verify(request: Request):
    """
    IP-based rate limiter for the /verify-image endpoint.
    
    Uses Redis INCR + EXPIRE to enforce a sliding window:
    - Key format: "rl:<client_ip>"
    - Max 5 requests per 60-second window per IP.
    - If Redis is down, the endpoint remains accessible (fail-open 
      for prototype; fail-closed in production).
    """
    r = _get_redis()
    if r is None:
        return  # Fail-open in dev mode

    client_ip = request.client.host
    key = f"rl:verify:{client_ip}"

    try:
        current_count = r.incr(key)
        if current_count == 1:
            # First request in window — set the expiry
            r.expire(key, RATE_LIMIT_WINDOW_SECONDS)

        if current_count > RATE_LIMIT_MAX_REQUESTS:
            ttl = r.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX_REQUESTS} "
                       f"verification requests per {RATE_LIMIT_WINDOW_SECONDS}s. "
                       f"Retry after {ttl}s.",
            )
    except redis.ConnectionError:
        return  # Redis went down mid-request; fail-open
