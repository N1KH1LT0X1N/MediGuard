#!/usr/bin/env python3
"""
Clear all data from Supabase database tables.
This script deletes all records from hash_chain, predictions, and users tables.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from backend.config.database import get_async_engine, get_database_url


async def clear_all_data():
    """Clear all data from database tables."""
    print("="*80)
    print("CLEARING SUPABASE DATA")
    print("="*80)
    
    # Check for DATABASE_URL
    database_url = get_database_url()
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is required.")
        print("\nPlease set up your .env file:")
        print("1. Create a .env file in the project root")
        print("2. Add DATABASE_URL from Supabase:")
        print("   DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres")
        print("\nSee docs/DATABASE_SETUP.md for detailed instructions.")
        return False
    
    try:
        engine = get_async_engine()
        
        print("\n🔌 Connecting to database...")
        
        async with engine.begin() as conn:
            # Get counts before deletion
            print("\n📊 Checking current data...")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM hash_chain"))
            hash_chain_count = result.scalar()
            
            result = await conn.execute(text("SELECT COUNT(*) FROM predictions"))
            predictions_count = result.scalar()
            
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            
            print(f"  - hash_chain: {hash_chain_count} records")
            print(f"  - predictions: {predictions_count} records")
            print(f"  - users: {users_count} records")
            
            if hash_chain_count == 0 and predictions_count == 0 and users_count == 0:
                print("\n✓ Database is already empty. Nothing to clear.")
                await engine.dispose()
                return True
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will delete ALL data from the database!")
            print(f"   - {hash_chain_count} hash chain records")
            print(f"   - {predictions_count} prediction records")
            print(f"   - {users_count} user records")
            
            # Delete in order (respecting foreign key constraints)
            print("\n🗑️  Deleting data...")
            
            # Delete hash_chain first (references predictions)
            if hash_chain_count > 0:
                print("  Deleting hash_chain records...")
                await conn.execute(text("DELETE FROM hash_chain"))
                print(f"  ✓ Deleted {hash_chain_count} hash_chain records")
            
            # Reset hash_chain sequence to start from 1
            print("  Resetting hash_chain sequence...")
            await conn.execute(text("ALTER SEQUENCE hash_chain_id_seq RESTART WITH 1"))
            print("  ✓ Hash chain sequence reset to 1")
            
            # Delete predictions (references users)
            if predictions_count > 0:
                print("  Deleting predictions records...")
                await conn.execute(text("DELETE FROM predictions"))
                print(f"  ✓ Deleted {predictions_count} prediction records")
            
            # Delete users last (base table)
            if users_count > 0:
                print("  Deleting users records...")
                await conn.execute(text("DELETE FROM users"))
                print(f"  ✓ Deleted {users_count} user records")
            
            # Verify deletion
            print("\n📊 Verifying deletion...")
            result = await conn.execute(text("SELECT COUNT(*) FROM hash_chain"))
            hash_chain_remaining = result.scalar()
            
            result = await conn.execute(text("SELECT COUNT(*) FROM predictions"))
            predictions_remaining = result.scalar()
            
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            users_remaining = result.scalar()
            
            if hash_chain_remaining == 0 and predictions_remaining == 0 and users_remaining == 0:
                print("✓ All data cleared successfully!")
                print("\nDatabase tables are now empty:")
                print("  - hash_chain: 0 records")
                print("  - predictions: 0 records")
                print("  - users: 0 records")
            else:
                print("⚠️  Warning: Some data may still remain:")
                print(f"  - hash_chain: {hash_chain_remaining} records")
                print(f"  - predictions: {predictions_remaining} records")
                print(f"  - users: {users_remaining} records")
        
        await engine.dispose()
        return True
        
    except ValueError as e:
        # Configuration error (missing/invalid DATABASE_URL)
        print(f"❌ Configuration error: {str(e)}")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to clear data: {error_msg}")
        
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
            print("  5. Try again")
        elif "authentication failed" in error_msg.lower():
            print("\n🔍 Authentication Error: Invalid credentials")
            print("Check your DATABASE_URL password is correct")
        elif "connection refused" in error_msg.lower():
            print("\n🔍 Connection Refused: Database server not reachable")
            print("Check that your Supabase project is active and the hostname is correct")
        
        return False


async def main():
    """Main function."""
    success = await clear_all_data()
    
    if success:
        print("\n" + "="*80)
        print("✓✓✓ DATA CLEARED SUCCESSFULLY! ✓✓✓")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO CLEAR DATA")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))

