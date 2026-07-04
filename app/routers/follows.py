from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models
from app.auth import get_current_user
from app.db import get_db

router = APIRouter(prefix="/users", tags=["follows"])


async def _get_user_or_404(db: AsyncSession, user_id: int) -> models.User:
    """Fetches a user by ID or raises a 404 HTTPException."""
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/{user_id}/follow", status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself",
        )
    target_user = await _get_user_or_404(db, user_id)

    stmt = select(models.Follow).where(
        models.Follow.follower_id == current_user.id,
        models.Follow.followed_id == user_id,
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user",
        )

    follow = models.Follow(follower_id=current_user.id, followed_id=user_id)
    db.add(follow)
    await db.commit()
    return {"detail": f"Now following {target_user.username}"}


@router.delete("/{user_id}/unfollow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unfollow yourself",
        )
    target_user = await _get_user_or_404(db, user_id)

    stmt = select(models.Follow).where(
        models.Follow.follower_id == current_user.id,
        models.Follow.followed_id == user_id,
    )
    existing = await db.execute(stmt)
    follow = existing.scalar_one_or_none()
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship does not exist",
        )

    await db.delete(follow)
    await db.commit()
    return {"detail": f"Unfollowed {target_user.username}"}


@router.get("/{user_id}/followers", response_model=List[schemas.UserRead])
async def list_followers(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_or_404(db, user_id)

    stmt = (
        select(models.User)
        .join(models.Follow, models.Follow.follower_id == models.User.id)
        .where(models.Follow.followed_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@router.get("/{user_id}/following", response_model=List[schemas.UserRead])
async def list_following(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_or_404(db, user_id)

    stmt = (
        select(models.User)
        .join(models.Follow, models.Follow.followed_id == models.User.id)
        .where(models.Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users