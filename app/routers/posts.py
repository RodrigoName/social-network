# app/routers/posts.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.auth import get_current_user
from app.db import get_db
from app.models import Post, Like, Follow, User
from app.utils import PaginationMeta, utc_now

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "",
    response_model=schemas.PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
async def create_post(
    payload: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_post = Post(user_id=current_user.id, content=payload.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return schemas.PostRead.from_orm(new_post)


@router.get(
    "/feed",
    response_model=schemas.PostRead,
    summary="Get the authenticated user's feed",
)
async def get_feed(
    page: int = Query(1, ge=1, description="Page number (1‑based)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # IDs of users the current user follows
    follow_stmt = select(Follow.followed_id).where(Follow.follower_id == current_user.id)
    result = await db.execute(follow_stmt)
    followed_ids = [row[0] for row in result.scalars().all()]

    # Include own posts as well
    relevant_user_ids = followed_ids + [current_user.id]

    # Total count
    count_stmt = select(func.count()).select_from(Post).where(Post.user_id.in_(relevant_user_ids))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Pagination
    offset = (page - 1) * size
    posts_stmt = (
        select(Post)
        .where(Post.user_id.in_(relevant_user_ids))
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    posts_result = await db.execute(posts_stmt)
    posts: List[Post] = posts_result.scalars().all()

    meta = PaginationMeta(total=total, page=page, size=size, pages=(total + size - 1) // size)
    return {"items": [schemas.PostRead.from_orm(p) for p in posts], "meta": meta}


@router.post(
    "/{post_id}/like",
    response_model=schemas.LikeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Like a post",
)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify post exists
    post_stmt = select(Post).where(Post.id == post_id)
    post_res = await db.execute(post_stmt)
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if already liked
    like_check = select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    like_res = await db.execute(like_check)
    existing_like = like_res.scalar_one_or_none()
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")

    new_like = Like(user_id=current_user.id, post_id=post_id, created_at=utc_now())
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    return schemas.LikeRead.from_orm(new_like)


@router.delete(
    "/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove like from a post",
)
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify like exists
    like_stmt = select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    like_res = await db.execute(like_stmt)
    like = like_res.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    await db.execute(delete(Like).where(Like.id == like.id))
    await db.commit()
    return None