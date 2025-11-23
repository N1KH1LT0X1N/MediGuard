"""
Database migration script.
Run this to create tables in Supabase database.
Alternatively, run schema.sql directly in Supabase SQL Editor.

Usage:
    From project root: python -m backend.database.migrate
    Or: cd backend && python -m database.migrate
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path so imports work
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.database import get_async_engine

SCHEMA_FILE = PROJECT_ROOT / "backend" / "database" / "schema.sql"


async def run_migration():
    """Run database migration."""
    # Check for DATABASE_URL
    if not os.getenv("DATABASE_URL"):
        print("❌ Error: DATABASE_URL environment variable is required.")
        print("\nPlease set up your .env file:")
        print("1. Create a .env file in the project root")
        print("2. Add DATABASE_URL from Supabase:")
        print("   DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres")
        print("\nOr set it directly:")
        print("   export DATABASE_URL='postgresql://...'")
        print("\nSee docs/DATABASE_SETUP.md for detailed instructions.")
        return
    
    try:
    engine = get_async_engine()
    
    # Read schema file
    if not SCHEMA_FILE.exists():
            print(f"❌ Error: Schema file not found at {SCHEMA_FILE}")
        return
    
        print("📄 Reading schema file...")
    schema_sql = SCHEMA_FILE.read_text()
    
        print("🔌 Connecting to database...")
    async with engine.begin() as conn:
        # Execute schema SQL
            print("📊 Creating tables...")
        await conn.execute(text(schema_sql))
            print("✓ Database migration completed successfully!")
            print("\nTables created:")
            print("  - users")
            print("  - predictions")
            print("  - hash_chain")
            print("  - All indexes")
    
    await engine.dispose()
    except ValueError as e:
        # Configuration error (missing/invalid DATABASE_URL)
        print(f"❌ Configuration error: {str(e)}")
        return
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Migration failed: {error_msg}")
        
        # Check for specific error types
        if "nodename nor servname provided" in error_msg or "gaierror" in error_msg:
            print("\n🔍 Connection Error: Cannot resolve database hostname")
            print("\n⚠️  MOST COMMON CAUSE: Supabase project is PAUSED")
            print("   Free tier projects pause after 7 days of inactivity")
            print("\n💡 Solution:")
            print("  1. Go to https://supabase.com/dashboard")
            print("  2. Find your project in the dashboard")
            print("  3. If it shows 'Paused', click 'Restore' or 'Resume'")
            print("  4. Wait 1-2 minutes for the project to restart")
            print("  5. Try the migration again")
            print("\n📋 Other possible causes:")
            print("  1. DATABASE_URL has an invalid hostname")
            print("  2. Network connectivity issues")
            print("  3. Hostname changed (get new connection string from Supabase)")
            print("\n🔧 To verify:")
            print("  - Run: python -m backend.database.validate_connection")
            print("  - Check Supabase dashboard for project status")
        elif "authentication failed" in error_msg.lower():
            print("\n🔍 Authentication Error: Invalid credentials")
            print("Check your DATABASE_URL password is correct")
        elif "connection refused" in error_msg.lower():
            print("\n🔍 Connection Refused: Database server not reachable")
            print("Check that your Supabase project is active and the hostname is correct")
        else:
            print("\nTroubleshooting:")
            print("1. Verify DATABASE_URL is correct")
            print("2. Check that your Supabase project is active")
            print("3. Ensure password is URL-encoded if it contains special characters")
            print("4. Try running schema.sql directly in Supabase SQL Editor")
        
        print("\n📝 Alternative: Run schema.sql in Supabase SQL Editor")
        print(f"   File location: {SCHEMA_FILE}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())

