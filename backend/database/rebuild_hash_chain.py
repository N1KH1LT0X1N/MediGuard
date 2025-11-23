#!/usr/bin/env python3
"""
Rebuild hash chain after data deletion.
This script resets the sequence and rebuilds hash chain entries for existing predictions.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config.database import get_async_engine, get_database_url, get_async_session_maker
from backend.models.database_models import Prediction, HashChain
from backend.services.hash_chain_service import HashChainService


async def rebuild_hash_chain():
    """Rebuild hash chain for all existing predictions."""
    print("="*80)
    print("REBUILDING HASH CHAIN")
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
        async_session_maker = get_async_session_maker()
        hash_chain_service = HashChainService()
        
        print("\n🔌 Connecting to database...")
        
        async with engine.begin() as conn:
            # Check current state
            print("\n📊 Checking current state...")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM hash_chain"))
            hash_chain_count = result.scalar()
            
            result = await conn.execute(text("SELECT COUNT(*) FROM predictions"))
            predictions_count = result.scalar()
            
            print(f"  - hash_chain entries: {hash_chain_count}")
            print(f"  - predictions: {predictions_count}")
            
            if predictions_count == 0:
                print("\n✓ No predictions found. Hash chain will be empty.")
                # Just reset the sequence
                print("\n🔄 Resetting hash_chain sequence...")
                await conn.execute(text("TRUNCATE TABLE hash_chain RESTART IDENTITY CASCADE"))
                print("  ✓ Sequence reset (table truncated)")
                await engine.dispose()
                return True
            
            # Get current sequence value
            result = await conn.execute(text(
                "SELECT last_value, is_called FROM hash_chain_id_seq"
            ))
            seq_info = result.fetchone()
            if seq_info:
                print(f"  - Current sequence: last_value={seq_info[0]}, is_called={seq_info[1]}")
            
            if hash_chain_count > 0:
                print(f"\n⚠️  WARNING: Found {hash_chain_count} existing hash chain entries.")
                print("   These will be deleted and rebuilt.")
                confirm = input("Type 'yes' to continue: ")
                if confirm.lower() != 'yes':
                    print("Rebuild cancelled.")
                    await engine.dispose()
                    return False
        
        # Now work with a session for ORM operations
        async with async_session_maker() as session:
            try:
                # Delete all existing hash chain entries
                if hash_chain_count > 0:
                    print("\n🗑️  Deleting existing hash chain entries...")
                    await session.execute(text("DELETE FROM hash_chain"))
                    await session.commit()
                    print(f"  ✓ Deleted {hash_chain_count} entries")
                
                # Reset the sequence
                print("\n🔄 Resetting sequence...")
                await session.execute(text("ALTER SEQUENCE hash_chain_id_seq RESTART WITH 1"))
                await session.commit()
                print("  ✓ Sequence reset to 1")
                
                # Get all predictions in chronological order
                print("\n📋 Fetching predictions in chronological order...")
                result = await session.execute(
                    select(Prediction)
                    .order_by(Prediction.timestamp.asc(), Prediction.created_at.asc())
                )
                predictions = result.scalars().all()
                
                if not predictions:
                    print("  ✓ No predictions to process")
                    await engine.dispose()
                    return True
                
                print(f"  ✓ Found {len(predictions)} predictions to process")
                
                # Rebuild hash chain
                print("\n🔗 Rebuilding hash chain...")
                previous_hash = None
                
                for i, prediction in enumerate(predictions, 1):
                    # Generate hash for this prediction
                    prediction_data = {
                        "input_features": prediction.input_features,
                        "prediction_result": prediction.prediction_result
                    }
                    
                    timestamp_str = prediction.timestamp.isoformat() if prediction.timestamp else prediction.created_at.isoformat()
                    
                    current_hash = hash_chain_service.generate_hash(
                        prediction_id=prediction.id,
                        user_id=prediction.user_id,
                        prediction_data=prediction_data,
                        timestamp=timestamp_str,
                        previous_hash=previous_hash
                    )
                    
                    # Create hash chain entry
                    hash_entry = HashChain(
                        prediction_id=prediction.id,
                        previous_hash=previous_hash,
                        current_hash=current_hash,
                        block_timestamp=prediction.timestamp or prediction.created_at
                    )
                    
                    session.add(hash_entry)
                    
                    if i % 10 == 0:
                        await session.flush()
                        print(f"  Processed {i}/{len(predictions)} predictions...")
                    
                    previous_hash = current_hash
                
                await session.commit()
                print(f"\n  ✓ Successfully rebuilt hash chain for {len(predictions)} predictions")
                
                # Verify the chain
                print("\n🔍 Verifying hash chain...")
                verification_result = await hash_chain_service.verify_chain(session)
                
                if verification_result["valid"]:
                    print("  ✓ Hash chain verification PASSED")
                    print(f"  - Total entries: {verification_result['total_entries']}")
                else:
                    print("  ❌ Hash chain verification FAILED")
                    print(f"  - Errors: {len(verification_result['errors'])}")
                    for error in verification_result['errors'][:5]:  # Show first 5 errors
                        print(f"    • {error}")
                    if len(verification_result['errors']) > 5:
                        print(f"    ... and {len(verification_result['errors']) - 5} more errors")
                
                await engine.dispose()
                return verification_result["valid"]
                
            except Exception as e:
                await session.rollback()
                raise e
        
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to rebuild hash chain: {error_msg}")
        import traceback
        traceback.print_exc()
        
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
    success = await rebuild_hash_chain()
    
    if success:
        print("\n" + "="*80)
        print("✓✓✓ HASH CHAIN REBUILT SUCCESSFULLY! ✓✓✓")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO REBUILD HASH CHAIN")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))

