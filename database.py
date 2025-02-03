from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/code_review_db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CodeReview(Base):
    """Model for storing code review results"""
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    review_date = Column(DateTime, default=datetime.utcnow)
    code_content = Column(Text)
    high_priority_issues = Column(JSON)
    medium_priority_issues = Column(JSON)
    low_priority_issues = Column(JSON)
    suggestions = Column(JSON)
    context = Column(JSON, nullable=True)

class ReviewInsight(Base):
    """Model for storing learned insights from reviews"""
    __tablename__ = "review_insights"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String, index=True)
    issue_type = Column(String, index=True)
    severity = Column(String)
    suggestion = Column(Text)
    frequency = Column(Integer, default=1)
    last_seen = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def store_review_result(
    file_path: str,
    code_content: str,
    review_result: Dict[str, Any],
    context: Optional[Dict] = None
) -> CodeReview:
    """
    Store code review results in the database
    
    Args:
        file_path: Path of the reviewed file
        code_content: Content of the reviewed code
        review_result: Results from the code review
        context: Additional context for the review
        
    Returns:
        CodeReview: Created database record
    """
    db = SessionLocal()
    try:
        review = CodeReview(
            file_path=file_path,
            code_content=code_content,
            high_priority_issues=review_result.get("high_priority", []),
            medium_priority_issues=review_result.get("medium_priority", []),
            low_priority_issues=review_result.get("low_priority", []),
            suggestions=review_result.get("suggestions", []),
            context=context
        )
        db.add(review)
        await update_insights(db, review_result)
        db.commit()
        db.refresh(review)
        return review
    finally:
        db.close()

async def update_insights(db, review_result: Dict[str, Any]):
    """
    Update review insights based on new review results
    
    Args:
        db: Database session
        review_result: Results from the code review
    """
    # Process high priority issues
    for issue in review_result.get("high_priority", []):
        insight = db.query(ReviewInsight).filter_by(
            pattern=issue.get("pattern", ""),
            issue_type=issue.get("type", "")
        ).first()
        
        if insight:
            insight.frequency += 1
            insight.last_seen = datetime.utcnow()
        else:
            insight = ReviewInsight(
                pattern=issue.get("pattern", ""),
                issue_type=issue.get("type", ""),
                severity="high",
                suggestion=issue.get("description", "")
            )
            db.add(insight)
    
    # Similar processing for medium and low priority issues
    # [Implementation similar to high priority processing]

async def get_review_history(file_path: Optional[str] = None, limit: int = 10):
    """
    Get review history from database
    
    Args:
        file_path: Optional file path to filter by
        limit: Maximum number of records to return
        
    Returns:
        List of review records
    """
    db = SessionLocal()
    try:
        query = db.query(CodeReview)
        if file_path:
            query = query.filter(CodeReview.file_path == file_path)
        return query.order_by(CodeReview.review_date.desc()).limit(limit).all()
    finally:
        db.close()

async def get_common_issues(min_frequency: int = 2):
    """
    Get commonly occurring issues
    
    Args:
        min_frequency: Minimum occurrence frequency
        
    Returns:
        List of common issues
    """
    db = SessionLocal()
    try:
        return db.query(ReviewInsight)\
                 .filter(ReviewInsight.frequency >= min_frequency)\
                 .order_by(ReviewInsight.frequency.desc())\
                 .all()
    finally:
        db.close() 