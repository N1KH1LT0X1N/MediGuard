"""
Background task for periodically committing hash chain root hashes to blockchain.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.database import get_async_session_maker, get_async_engine
from backend.services.hash_chain_service import HashChainService
from backend.services.blockchain_service import BlockchainService
from backend.models.database_models import HashChain
from sqlalchemy import select, update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainCommitter:
    """Background task for committing hash chain to blockchain."""
    
    def __init__(
        self,
        blockchain_service: BlockchainService,
        commit_interval_hours: int = 24
    ):
        """
        Initialize blockchain committer.
        
        Args:
            blockchain_service: BlockchainService instance
            commit_interval_hours: Hours between commits (default: 24)
        """
        self.blockchain_service = blockchain_service
        self.commit_interval_hours = commit_interval_hours
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.hash_chain_service = HashChainService()
        self.async_session_maker = get_async_session_maker()
        self.engine = get_async_engine()
    
    async def commit_pending_hashes(self):
        """
        Commit all pending hashes (those without blockchain_tx_hash) to blockchain.
        """
        async with self.async_session_maker() as session:
            try:
                # Get all hash chain entries without blockchain transaction
                result = await session.execute(
                    select(HashChain)
                    .where(HashChain.blockchain_tx_hash.is_(None))
                    .order_by(HashChain.id.asc())
                )
                pending_entries = result.scalars().all()
                
                if not pending_entries:
                    logger.info("No pending hashes to commit to blockchain")
                    return
                
                logger.info(f"Found {len(pending_entries)} pending hash(es) to commit")
                
                # Get the latest hash (root of chain)
                latest_hash = await self.hash_chain_service.get_latest_hash(session)
                
                if not latest_hash:
                    logger.warning("No hash chain entries found")
                    return
                
                # Commit root hash to blockchain
                mode = getattr(self.blockchain_service, 'mode', 'unknown')
                mode_text = "simulated blockchain" if mode == "simulated" else "blockchain"
                logger.info(f"Committing root hash {latest_hash} to {mode_text}...")
                result = self.blockchain_service.commit_hash_to_blockchain(
                    root_hash=latest_hash,
                    metadata={
                        "total_entries": len(pending_entries),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                if result["success"]:
                    # Update all pending entries with transaction hash
                    tx_hash = result["tx_hash"]
                    block_number = result["block_number"]
                    
                    await session.execute(
                        update(HashChain)
                        .where(HashChain.blockchain_tx_hash.is_(None))
                        .values(
                            blockchain_tx_hash=tx_hash,
                            blockchain_block_number=block_number
                        )
                    )
                    await session.commit()
                    
                    mode_note = " (simulated)" if mode == "simulated" else ""
                    logger.info(
                        f"✓ Successfully committed hash to {mode_text}{mode_note}. "
                        f"TX: {tx_hash}, Block: {block_number}"
                    )
                else:
                    logger.error(f"✗ Failed to commit hash to blockchain: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error committing hashes to blockchain: {str(e)}")
                await session.rollback()
    
    async def run_periodic_commits(self):
        """Run periodic blockchain commits in background."""
        self.is_running = True
        logger.info(f"Blockchain committer started. Interval: {self.commit_interval_hours} hours")
        
        while self.is_running:
            try:
                await self.commit_pending_hashes()
            except Exception as e:
                logger.error(f"Error in periodic commit: {str(e)}")
            
            # Wait for next interval
            await asyncio.sleep(self.commit_interval_hours * 3600)
    
    def start(self):
        """Start the background task."""
        if not self.is_running:
            self.task = asyncio.create_task(self.run_periodic_commits())
            logger.info("Blockchain committer task started")
    
    def stop(self):
        """Stop the background task."""
        self.is_running = False
        if self.task:
            self.task.cancel()
            logger.info("Blockchain committer task stopped")


# Global instance (will be initialized in main.py)
blockchain_committer: Optional[BlockchainCommitter] = None

