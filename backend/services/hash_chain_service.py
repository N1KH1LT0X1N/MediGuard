"""
Hash Chain Service for creating immutable audit trail of predictions.
"""

import hashlib
import json
from typing import Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models.database_models import HashChain, Prediction


class HashChainService:
    """Service for managing hash chain of predictions."""
    
    @staticmethod
    def generate_hash(
        prediction_id: str,
        user_id: str,
        prediction_data: Dict,
        timestamp: str,
        previous_hash: Optional[str] = None
    ) -> str:
        """
        Generate SHA256 hash for a prediction.
        
        Args:
            prediction_id: UUID of the prediction
            user_id: User identifier
            prediction_data: Full prediction data (input_features + prediction_result)
            timestamp: ISO timestamp string
            previous_hash: Hash of previous entry in chain (None for first entry)
            
        Returns:
            SHA256 hash as hex string
        """
        # Create data string for hashing
        data_string = json.dumps({
            "prediction_id": prediction_id,
            "user_id": user_id,
            "prediction_data": prediction_data,
            "timestamp": timestamp,
            "previous_hash": previous_hash
        }, sort_keys=True)  # sort_keys ensures consistent ordering
        
        # Generate SHA256 hash
        hash_obj = hashlib.sha256(data_string.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    async def get_latest_hash(session: AsyncSession) -> Optional[str]:
        """
        Get the most recent hash from the chain.
        
        Args:
            session: Database session
            
        Returns:
            Most recent hash or None if chain is empty
        """
        result = await session.execute(
            select(HashChain.current_hash)
            .order_by(HashChain.id.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row
    
    @staticmethod
    async def add_to_chain(
        session: AsyncSession,
        prediction_id: str,
        user_id: str,
        input_features: Dict,
        prediction_result: Dict,
        timestamp: str
    ) -> Tuple[str, str]:
        """
        Add a prediction to the hash chain.
        
        Args:
            session: Database session
            prediction_id: UUID of the prediction
            user_id: User identifier
            input_features: Input features dictionary
            prediction_result: Prediction result dictionary
            timestamp: ISO timestamp string
            
        Returns:
            Tuple of (current_hash, previous_hash)
        """
        # Get previous hash
        previous_hash = await HashChainService.get_latest_hash(session)
        
        # Combine input_features and prediction_result for hashing
        prediction_data = {
            "input_features": input_features,
            "prediction_result": prediction_result
        }
        
        # Generate current hash
        current_hash = HashChainService.generate_hash(
            prediction_id=prediction_id,
            user_id=user_id,
            prediction_data=prediction_data,
            timestamp=timestamp,
            previous_hash=previous_hash
        )
        
        # Parse timestamp
        try:
            if 'Z' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif '+' in timestamp or (timestamp.count('-') > 2 and 'T' in timestamp):
                dt = datetime.fromisoformat(timestamp)
            else:
                dt = datetime.fromisoformat(timestamp)
        except Exception:
            dt = datetime.utcnow()
        
        # Create hash chain entry
        hash_entry = HashChain(
            prediction_id=prediction_id,
            previous_hash=previous_hash,
            current_hash=current_hash,
            block_timestamp=dt
        )
        
        session.add(hash_entry)
        await session.flush()  # Flush to get the ID
        
        return current_hash, previous_hash
    
    @staticmethod
    async def verify_chain(session: AsyncSession) -> Dict:
        """
        Verify the integrity of the hash chain.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with verification results
        """
        # Get all hash chain entries ordered by ID
        result = await session.execute(
            select(HashChain)
            .order_by(HashChain.id.asc())
        )
        entries = result.scalars().all()
        
        if not entries:
            return {
                "valid": True,
                "message": "Hash chain is empty",
                "total_entries": 0,
                "errors": []
            }
        
        errors = []
        previous_hash = None
        
        for i, entry in enumerate(entries):
            # Get the prediction to verify hash
            pred_result = await session.execute(
                select(Prediction)
                .where(Prediction.id == entry.prediction_id)
            )
            prediction = pred_result.scalar_one_or_none()
            
            if not prediction:
                errors.append(f"Entry {i+1}: Prediction {entry.prediction_id} not found")
                continue
            
            # Verify previous hash link
            if i > 0 and entry.previous_hash != previous_hash:
                errors.append(
                    f"Entry {i+1}: Previous hash mismatch. "
                    f"Expected {previous_hash}, got {entry.previous_hash}"
                )
            
            # Recalculate hash to verify
            prediction_data = {
                "input_features": prediction.input_features,
                "prediction_result": prediction.prediction_result
            }
            
            expected_hash = HashChainService.generate_hash(
                prediction_id=prediction.id,
                user_id=prediction.user_id,
                prediction_data=prediction_data,
                timestamp=prediction.timestamp.isoformat(),
                previous_hash=entry.previous_hash
            )
            
            if expected_hash != entry.current_hash:
                errors.append(
                    f"Entry {i+1}: Hash mismatch. "
                    f"Expected {expected_hash}, got {entry.current_hash}"
                )
            
            previous_hash = entry.current_hash
        
        return {
            "valid": len(errors) == 0,
            "message": "Hash chain verification complete",
            "total_entries": len(entries),
            "errors": errors
        }
    
    @staticmethod
    async def get_chain_root_hash(session: AsyncSession) -> Optional[str]:
        """
        Get the root hash (most recent hash) for blockchain commitment.
        
        Args:
            session: Database session
            
        Returns:
            Most recent hash or None
        """
        return await HashChainService.get_latest_hash(session)

