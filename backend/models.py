from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from backend.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)  # twitter, linkedin, threads
    content = Column(Text)
    status = Column(String, default="draft")  # draft, queued, published, rejected
    brand_voice = Column(String)
    topic = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # when to publish


class PostFeedback(Base):
    __tablename__ = "post_feedback"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    action = Column(String)  # approved, edited, rejected
    edited_content = Column(Text, nullable=True)  # if edited, store the edited version
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class TrendCache(Base):
    __tablename__ = "trend_cache"

    id = Column(Integer, primary_key=True, index=True)
    geo = Column(String, index=True)  # geographic region (e.g., "US", "UK")
    hl = Column(String, index=True)   # language code (e.g., "en", "es")
    trends_data = Column(Text)  # JSON string containing trend data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # cache expiration time
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        from datetime import datetime
        return datetime.now(self.created_at.tzinfo) > self.expires_at
