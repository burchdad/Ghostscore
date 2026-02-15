"""
SQLAlchemy models for GhostScore
Maps to database schema
"""

from sqlalchemy import Column, String, Float, Date, DateTime, Integer, ForeignKey, Text, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profiles = relationship("CreditProfile", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class CreditProfile(Base):
    __tablename__ = "credit_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profiles")
    accounts = relationship("Account", back_populates="profile", cascade="all, delete-orphan")
    derogatories = relationship("Derogatory", back_populates="profile", cascade="all, delete-orphan")
    score_history = relationship("ScoreHistory", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CreditProfile {self.id}>"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("credit_profiles.id"), nullable=False)
    type = Column(String(50), nullable=False)  # credit_card, loan, mortgage, etc.
    name = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)
    limit = Column(Float, nullable=True)  # NULL for non-revolving accounts
    open_date = Column(Date, nullable=False)
    status = Column(String(50), default="active")  # active, closed, charged_off
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("CreditProfile", back_populates="accounts")

    def __repr__(self):
        return f"<Account {self.name}>"


class Derogatory(Base):
    __tablename__ = "derogatories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("credit_profiles.id"), nullable=False)
    type = Column(String(50), nullable=False)  # late_payment, collection, bankruptcy, etc.
    date = Column(Date, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("CreditProfile", back_populates="derogatories")

    def __repr__(self):
        return f"<Derogatory {self.type}>"


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("credit_profiles.id"), nullable=False)
    score = Column(Integer, nullable=False)
    payment_history = Column(Integer, nullable=True)
    utilization = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    new_credit = Column(Integer, nullable=True)
    mix = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("CreditProfile", back_populates="score_history")

    def __repr__(self):
        return f"<ScoreHistory score={self.score}>"
