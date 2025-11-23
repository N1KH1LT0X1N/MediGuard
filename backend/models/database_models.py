"""
SQLAlchemy database models for predictions and hash chain.
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """User model for storing user information and preferences."""
    
    __tablename__ = "users"
    
    id = Column(Text, primary_key=True)  # user_id from API
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    preferences = Column(JSONB, nullable=True)  # User preferences (theme, notifications, etc.)
    user_metadata = Column("metadata", JSONB, nullable=True)  # Additional user metadata (stored as 'metadata' in DB)
    
    # Relationship to predictions
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "preferences": self.preferences or {},
            "metadata": self.user_metadata or {}
        }


class Prediction(Base):
    """Prediction model for storing AI predictions."""
    
    __tablename__ = "predictions"
    
    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    source = Column(Text, nullable=False)  # manual, pdf, csv, image
    input_features = Column(JSONB, nullable=False)
    prediction_result = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    hash_chain_entry = relationship("HashChain", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "input_features": self.input_features,
            "prediction_result": self.prediction_result,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class HashChain(Base):
    """Hash chain model for immutable audit trail."""
    
    __tablename__ = "hash_chain"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Text, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_hash = Column(Text, nullable=True, index=True)
    current_hash = Column(Text, nullable=False, unique=True, index=True)
    block_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    blockchain_tx_hash = Column(Text, nullable=True, index=True)
    blockchain_block_number = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationship to prediction
    prediction = relationship("Prediction", back_populates="hash_chain_entry")
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "prediction_id": self.prediction_id,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "block_timestamp": self.block_timestamp.isoformat() if self.block_timestamp else None,
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "blockchain_block_number": self.blockchain_block_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

