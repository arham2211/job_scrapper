import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, expression
from sqlalchemy import Boolean
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Database URL, default to psycopg2 one if available for synchronous usage
# Note: The prompt provided asyncpg for DATABASE_URL, but we are writing a sync script first.
# We will use DIRECT_DATABASE_URL which uses psycopg2.
SQLALCHEMY_DATABASE_URL = os.getenv("DIRECT_DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DIRECT_DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # 'seek' or 'jobsearch'
    job_title = Column(String, index=True)
    company_name = Column(String, index=True)
    location = Column(String, index=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, default="Australia")
    is_remote = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    classification = Column(String, nullable=True)
    work_type = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    min_annual_salary = Column(Float, nullable=True)
    max_annual_salary = Column(Float, nullable=True)
    # posting_time = Column(String, nullable=True)
    posted_date = Column(Date, nullable=True)
    job_description = Column(Text, nullable=True)
    url = Column(String, unique=True, index=True) # Unique constraint to prevent duplicates
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def init_db():
    """Create tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
