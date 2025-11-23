"""
Prediction Storage Service for saving and retrieving prediction history.
Uses PostgreSQL database with hash chain for immutable audit trail.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.config.database import get_async_session_maker, get_async_engine
from backend.models.database_models import User, Prediction, HashChain, Base
from backend.services.hash_chain_service import HashChainService


class PredictionStorageService:
    """Service for storing and retrieving prediction history with hash chain."""
    
    def __init__(self):
        """Initialize prediction storage service."""
        self.async_session_maker = get_async_session_maker()
        self.hash_chain_service = HashChainService()
    
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            engine = get_async_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            # If connection fails, tables might already exist (created via SQL Editor)
            # This is not critical - tables will be created on first use if needed
            print(f"⚠️  Could not auto-create tables (they may already exist): {str(e)[:200]}")
    
    async def save_prediction(
        self,
        user_id: str,
        input_features: Dict[str, float],
        prediction_result: Dict,
        source: str = "manual"
    ) -> str:
        """
        Save a prediction to storage with hash chain entry.
        
        Args:
            user_id: User identifier
            input_features: Raw input features dictionary
            prediction_result: Full prediction response dictionary
            source: Source of the prediction (manual, pdf, csv, image)
            
        Returns:
            Prediction ID (UUID)
        """
        prediction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        async with self.async_session_maker() as session:
            try:
                # Ensure user exists in database
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    # Create user if doesn't exist
                    user = User(
                        id=user_id,
                        preferences={},
                        metadata={}
                    )
                    session.add(user)
                    await session.flush()
                
                # Parse timestamp
                try:
                    if 'Z' in timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    elif '+' in timestamp or timestamp.count('-') > 2:
                        dt = datetime.fromisoformat(timestamp)
                    else:
                        dt = datetime.fromisoformat(timestamp)
                except:
                    dt = datetime.utcnow()
                
                # Create prediction record
                prediction = Prediction(
                    id=prediction_id,
                    user_id=user_id,
                    timestamp=dt,
                    source=source,
                    input_features=input_features,
                    prediction_result=prediction_result
                )
                
                session.add(prediction)
                await session.flush()  # Flush to ensure prediction is in DB
                
                # Add to hash chain
                current_hash, previous_hash = await self.hash_chain_service.add_to_chain(
                    session=session,
                    prediction_id=prediction_id,
                    user_id=user_id,
                    input_features=input_features,
                    prediction_result=prediction_result,
                    timestamp=timestamp
                )
                
                await session.commit()
                return prediction_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Error saving prediction: {str(e)}")
    
    async def get_predictions(
        self,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get predictions, optionally filtered by user_id.
        Optimized: Default limit for performance.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Optional limit on number of results (default: 100 for performance)
            
        Returns:
            List of prediction records
        """
        async with self.async_session_maker() as session:
            try:
                # Default limit for performance (dashboard only needs recent predictions)
                effective_limit = limit if limit is not None else 100
                
                query = select(Prediction)
                
                if user_id:
                    query = query.where(Prediction.user_id == user_id)
                
                # Order by timestamp DESC (most recent first) before limiting
                query = query.order_by(Prediction.timestamp.desc()).limit(effective_limit)
                
                result = await session.execute(query)
                predictions = result.scalars().all()
                
                return [pred.to_dict() for pred in predictions]
                
            except Exception as e:
                raise Exception(f"Error retrieving predictions: {str(e)}")
    
    async def get_recent_predictions(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent predictions.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Number of recent predictions to return
            
        Returns:
            List of recent prediction records
        """
        return await self.get_predictions(user_id=user_id, limit=limit)
    
    async def get_unique_users(self, limit: Optional[int] = None) -> List[str]:
        """
        Get list of unique user IDs who have predictions.
        Optimized: Uses DISTINCT query instead of loading all predictions.
        
        Args:
            limit: Optional limit on number of users
            
        Returns:
            List of unique user IDs
        """
        async with self.async_session_maker() as session:
            try:
                from sqlalchemy import func, distinct
                
                query = select(distinct(Prediction.user_id))
                query = query.order_by(Prediction.user_id)
                
                if limit:
                    query = query.limit(limit)
                
                result = await session.execute(query)
                user_ids = [row[0] for row in result.fetchall() if row[0]]
                
                return user_ids
            except Exception as e:
                raise Exception(f"Error retrieving unique users: {str(e)}")
    
    async def get_dashboard_stats(self, user_id: Optional[str] = None) -> Dict:
        """
        Get aggregated statistics for dashboard.
        OPTIMIZED: Uses PostgreSQL JSONB aggregation functions (database-level, not Python loops).
        This is MUCH faster than loading and processing in Python.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary with aggregated statistics
        """
        async with self.async_session_maker() as session:
            try:
                from sqlalchemy import func, text
                from sqlalchemy.dialects.postgresql import JSONB
                
                # Get total count (fast)
                count_query = select(func.count(Prediction.id))
                if user_id:
                    count_query = count_query.where(Prediction.user_id == user_id)
                
                count_result = await session.execute(count_query)
                total_predictions = count_result.scalar() or 0
                
                if total_predictions == 0:
                    return {
                        "total_predictions": 0,
                        "disease_distribution": {},
                        "risk_levels": {
                            "high": 0,
                            "medium": 0,
                            "low": 0
                        },
                        "abnormal_features_summary": {}
                    }
                
                # SUPABASE OPTIMIZATION: Use PostgreSQL JSONB aggregation functions
                # This computes stats in the database, not in Python (10-100x faster)
                # Limit to 300 most recent for stats (reduced from 500)
                if user_id:
                    stats_query = text("""
                        WITH recent_predictions AS (
                            SELECT prediction_result
                            FROM predictions
                            WHERE user_id = :user_id
                            ORDER BY timestamp DESC
                            LIMIT 300
                        ),
                        disease_counts AS (
                            SELECT 
                                COALESCE(prediction_result->>'predicted_disease', 'Unknown') as disease,
                                COUNT(*)::int as count
                            FROM recent_predictions
                            WHERE prediction_result->>'predicted_disease' IS NOT NULL
                            GROUP BY COALESCE(prediction_result->>'predicted_disease', 'Unknown')
                        )
                        SELECT
                            -- Disease distribution (from subquery to avoid nested aggregates)
                            (SELECT COALESCE(jsonb_object_agg(disease, count), '{}'::jsonb) FROM disease_counts) as disease_dist,
                            
                            -- Risk levels (using JSONB path queries)
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) >= 0.7
                            ) as high_risk,
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) >= 0.5
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) < 0.7
                            ) as medium_risk,
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) < 0.5
                            ) as low_risk
                        FROM recent_predictions
                    """)
                    result = await session.execute(stats_query, {"user_id": user_id})
                else:
                    stats_query = text("""
                        WITH recent_predictions AS (
                            SELECT prediction_result
                            FROM predictions
                            ORDER BY timestamp DESC
                            LIMIT 300
                        ),
                        disease_counts AS (
                            SELECT 
                                COALESCE(prediction_result->>'predicted_disease', 'Unknown') as disease,
                                COUNT(*)::int as count
                            FROM recent_predictions
                            WHERE prediction_result->>'predicted_disease' IS NOT NULL
                            GROUP BY COALESCE(prediction_result->>'predicted_disease', 'Unknown')
                        )
                        SELECT
                            -- Disease distribution (from subquery to avoid nested aggregates)
                            (SELECT COALESCE(jsonb_object_agg(disease, count), '{}'::jsonb) FROM disease_counts) as disease_dist,
                            
                            -- Risk levels (using JSONB path queries)
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) >= 0.7
                            ) as high_risk,
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) >= 0.5
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) < 0.7
                            ) as medium_risk,
                            COUNT(*) FILTER (
                                WHERE (prediction_result->'probabilities')::text IS NOT NULL
                                AND (
                                    SELECT MAX(value::numeric)
                                    FROM jsonb_each(prediction_result->'probabilities')
                                ) < 0.5
                            ) as low_risk
                        FROM recent_predictions
                    """)
                    result = await session.execute(stats_query)
                
                row = result.fetchone()
                
                # Parse disease distribution
                disease_dist = row[0] if row[0] else {}
                
                # Risk levels
                risk_levels = {
                    "high": row[1] or 0,
                    "medium": row[2] or 0,
                    "low": row[3] or 0
                }
                
                # For abnormal features, we still need to process (but only from limited set)
                # This is acceptable since it's a smaller dataset now
                abnormal_query = select(Prediction.prediction_result)
                if user_id:
                    abnormal_query = abnormal_query.where(Prediction.user_id == user_id)
                abnormal_query = abnormal_query.order_by(Prediction.timestamp.desc()).limit(200)
                
                abnormal_result = await session.execute(abnormal_query)
                abnormal_features_count = {}
                
                for result_data in abnormal_result.scalars().all():
                    if not result_data:
                        continue
                    explainability = result_data.get("explainability_json", {})
                    if explainability:
                        for feature_name, importance in explainability.items():
                            if abs(importance) > 0.1:
                                abnormal_features_count[feature_name] = abnormal_features_count.get(feature_name, 0) + 1
                
                return {
                    "total_predictions": total_predictions,
                    "disease_distribution": disease_dist,
                    "risk_levels": risk_levels,
                    "abnormal_features_summary": abnormal_features_count
                }
                
            except Exception as e:
                raise Exception(f"Error retrieving dashboard stats: {str(e)}")
    
    async def verify_hash_chain(self) -> Dict:
        """
        Verify the integrity of the hash chain.
        
        Returns:
            Dictionary with verification results
        """
        async with self.async_session_maker() as session:
            return await self.hash_chain_service.verify_chain(session)
    
    async def get_prediction_by_id(self, prediction_id: str) -> Optional[Dict]:
        """
        Get a single prediction by ID.
        
        Args:
            prediction_id: Prediction UUID
            
        Returns:
            Prediction record or None
        """
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(Prediction).where(Prediction.id == prediction_id)
                )
                prediction = result.scalar_one_or_none()
                return prediction.to_dict() if prediction else None
            except Exception as e:
                raise Exception(f"Error retrieving prediction: {str(e)}")


# Global instance (will be initialized in main.py)
prediction_storage: Optional[PredictionStorageService] = None
