from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, db
from pydantic import BaseModel

router = APIRouter()


class PostBase(BaseModel):
    platform: str
    content: str
    status: str
    brand_voice: str
    topic: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    content: str
    status: str  # approved, rejected, or draft when edited


class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


@router.get("/", response_model=List[Post])
def get_posts_for_review(
    skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)
):
    # Get posts that are in draft status for review
    posts = (
        db_session.query(models.Post)
        .filter(models.Post.status == "draft")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts


@router.put("/{post_id}", response_model=Post)
def update_post_status(
    post_id: int, post_update: PostUpdate, db_session: Session = Depends(db.get_db)
):
    db_post = db_session.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update the post
    db_post.content = post_update.content
    db_post.status = post_update.status

    # If status is approved, set it to queued for publishing
    if post_update.status == "approved":
        db_post.status = "queued"
    elif post_update.status == "rejected":
        db_post.status = "rejected"
    # If edited but not explicitly approved/rejected, keep as draft

    db_session.commit()
    db_session.refresh(db_post)
    return db_post
