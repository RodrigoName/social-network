# app/auth.py
import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from app import schemas
from app.config import settings
from app.db import get_db
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession

# ----------------------------------------------------------------------
# Password hashing utilities
# ----------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------------------------------------------------
# JWT token utilities
# ----------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def _create_expiration(delta: Optional[datetime.timedelta] = None) -> datetime.datetime:
    """Calculate token expiration datetime."""
    if delta is None:
        delta = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return datetime.datetime.utcnow() + delta


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Create a JWT token embedding `data` and an expiration claim.
    """
    to_encode = data.copy()
    expire = _create_expiration(expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


# ----------------------------------------------------------------------
# Dependency to retrieve the current authenticated user
# ----------------------------------------------------------------------
async def _get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Fetch a user instance by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode the JWT token, verify its validity and return the corresponding User.
    Raises HTTPException 401 if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await _get_user_by_username(db, token_data.username)  # type: ignore[arg-type]
    if user is None:
        raise credentials_exception
    return user


__all__ = [
    "pwd_context",
    "get_password_hash",
    "verify_password",
    "oauth2_scheme",
    "create_access_token",
    "get_current_user",
]