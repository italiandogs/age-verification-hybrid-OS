import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup for handling user data
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Define User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(50), nullable=False)   # Only collecting discord_id
    verification_status = Column(Boolean, default=False)
    dob = Column(Date, nullable=True)  # Collecting Date of Birth for age verification
    last_verification_attempt = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

# Create the table
Base.metadata.create_all(engine)

def create_user(discord_id, dob):
    """Creates a new user with their Discord ID and Date of Birth."""
    with session_scope() as session:
        new_user = User(discord_id=discord_id, dob=dob, verification_status=False)
        session.add(new_user)

def update_user_verification_status(discord_id, status=True):
    """Update verification status after age verification."""
    with session_scope() as session:
        user = session.query(User).filter_by(discord_id=discord_id).first()
        if user:
            user.verification_status = status

def get_user_by_discord_id(discord_id):
    """Retrieve user info by Discord ID."""
    with session_scope() as session:
        return session.query(User).filter_by(discord_id=discord_id).first()

def set_verification_attempt(discord_id):
    """Update the last verification attempt."""
    with session_scope() as session:
        user = session.query(User).filter_by(discord_id=discord_id).first()
        if user:
            user.last_verification_attempt = datetime.now(timezone.utc)
