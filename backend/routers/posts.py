from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, db
from pydantic import BaseModel

router = APIRouter()


class PostBase(BaseModel):
    platform: str
    content: str
    status: str = "draft"
    brand_voice: str
    topic: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


@router.get("/", response_model=List[Post])
def get_posts(
    skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)
):
    posts = db_session.query(models.Post).offset(skip).limit(limit).all()
    return posts


@router.post("/", response_model=Post)
def create_post(post: PostCreate, db_session: Session = Depends(db.get_db)):
    db_post = models.Post(**post.dict())
    db_session.add(db_post)
    db_session.commit()
    db_session.refresh(db_post)
    return db_post


@router.put("/{post_id}", response_model=Post)
def update_post(
    post_id: int, post: PostCreate, db_session: Session = Depends(db.get_db)
):
    db_post = db_session.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db_session.commit()
    db_session.refresh(db_post)
    return db_post


@router.delete("/{post_id}")
def delete_post(post_id: int, db_session: Session = Depends(db.get_db)):
    db_post = db_session.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_session.delete(db_post)
    db_session.commit()
    return {"message": "Post deleted"}
