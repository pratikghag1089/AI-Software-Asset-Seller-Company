"""
Database models for Prog Silo Company autonomous LinkedIn agent
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Post(Base):
    """LinkedIn posts created by the system"""
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    topic = Column(String(255))
    posted_at = Column(DateTime, default=datetime.utcnow)

    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Metadata
    posted_by_agent = Column(Boolean, default=True)
    agent_version = Column(String(50))
    quality_score = Column(Float)

    # Relationships
    learnings = relationship("Learning", back_populates="post")


class Comment(Base):
    """Comments made by engagement agent"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    post_url = Column(Text, nullable=False)
    post_author = Column(String(255))
    comment_text = Column(Text, nullable=False)
    commented_at = Column(DateTime, default=datetime.utcnow)

    # Engagement metrics
    likes = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    author_replied = Column(Boolean, default=False)
    profile_visits_after = Column(Integer, default=0)

    # Metadata
    quality_score = Column(Float)
    strategy_used = Column(String(255))


class Metric(Base):
    """Daily metrics tracking"""
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, unique=True)

    # Profile metrics
    followers = Column(Integer, default=0)
    follower_change = Column(Integer, default=0)
    profile_views = Column(Integer, default=0)
    search_appearances = Column(Integer, default=0)

    # Content metrics
    posts_published = Column(Integer, default=0)
    avg_post_views = Column(Float, default=0.0)
    avg_engagement_rate = Column(Float, default=0.0)

    # Engagement metrics
    comments_made = Column(Integer, default=0)
    comment_reply_rate = Column(Float, default=0.0)
    connections_made = Column(Integer, default=0)


class Learning(Base):
    """Insights learned by the Learning Agent"""
    __tablename__ = 'learnings'

    id = Column(Integer, primary_key=True)
    learned_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100))  # 'content', 'engagement', 'timing', 'strategy'
    insight = Column(Text, nullable=False)
    confidence = Column(Float)  # 0.0 to 1.0

    # Supporting data
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)
    data_points = Column(Integer)  # How many observations support this

    # Lifecycle
    active = Column(Boolean, default=True)
    applied_count = Column(Integer, default=0)

    # Relationships
    post = relationship("Post", back_populates="learnings")


class AgentRun(Base):
    """Track agent executions"""
    __tablename__ = 'agent_runs'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Results
    success = Column(Boolean)
    task = Column(Text)
    result = Column(Text)
    error = Column(Text, nullable=True)

    # Resource usage
    tokens_used = Column(Integer, default=0)
    execution_time_seconds = Column(Float)


class Strategy(Base):
    """Current strategy configuration"""
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    # Content strategy
    content_themes = Column(Text)  # JSON array
    preferred_post_types = Column(Text)  # JSON array
    posting_time = Column(String(10))

    # Engagement strategy
    target_hashtags = Column(Text)  # JSON array
    target_follower_range_min = Column(Integer)
    target_follower_range_max = Column(Integer)
    comments_per_day = Column(Integer)

    # Goals
    daily_follower_target = Column(Integer)
    engagement_rate_target = Column(Float)

    # Performance
    strategy_score = Column(Float, default=0.0)  # How well is it working


# Database initialization
def init_db(database_url=None):
    """Initialize database and create all tables"""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///progsilo.db')

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    """Get database session"""
    if engine is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///progsilo.db')
        engine = create_engine(database_url)

    Session = sessionmaker(bind=engine)
    return Session()
