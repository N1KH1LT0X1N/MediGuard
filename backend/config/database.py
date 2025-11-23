"""
Database configuration and connection setup for Supabase PostgreSQL.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load .env from project root (parent of backend directory)
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
env_path = PROJECT_ROOT / ".env"
load_dotenv(env_path)

# Supabase connection details
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_database_url():
    """Get DATABASE_URL from environment, reloading if needed."""
    # Reload .env to get latest value
    load_dotenv(env_path, override=True)
    return os.getenv("DATABASE_URL")

def get_async_database_url():
    """Get async database URL, reading fresh from environment."""
    database_url = get_database_url()
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required.\n"
            "Get it from Supabase project settings -> Database -> Connection string.\n"
            "Format: postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres"
        )
    
    # Validate DATABASE_URL format
    if not database_url.startswith("postgresql://"):
        raise ValueError(
            f"DATABASE_URL must start with 'postgresql://'. "
            f"Current value starts with: {database_url[:20]}..."
        )
    
    # DATABASE_URL format: postgresql://user:password@host:port/database
    # For async: postgresql+asyncpg://user:password@host:port/database
    return database_url.replace("postgresql://", "postgresql+asyncpg://")


# Global engine instances (initialized on first use)
_async_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker] = None


def get_async_engine() -> AsyncEngine:
    """Create asynchronous SQLAlchemy engine."""
    global _async_engine, _async_session_maker
    
    # Always dispose old engine and create new one to ensure fresh connection
    if _async_engine is not None:
        # Dispose old engine to force recreation with new URL
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't await in sync context, just clear the reference
                _async_engine = None
                _async_session_maker = None
            else:
                asyncio.run(_async_engine.dispose())
                _async_engine = None
                _async_session_maker = None
        except:
            _async_engine = None
            _async_session_maker = None
    
    # Always read fresh from environment
    async_url = get_async_database_url()
    
    _async_engine = create_async_engine(
        async_url,
        poolclass=NullPool,
        echo=False,
        future=True
    )
    return _async_engine


def get_async_session_maker() -> async_sessionmaker:
    """Get async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_async_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session_maker


async def close_db_connections():
    """Close all database connections."""
    global _async_engine, _async_session_maker
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        _async_session_maker = None

