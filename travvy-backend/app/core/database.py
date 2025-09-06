"""
Database Configuration and Utilities

This module handles Google Cloud Firestore initialization, connection management,
and common database operations with caching support.
"""

from google.cloud import firestore
from google.cloud.firestore import AsyncClient
from google.oauth2 import service_account
import redis.asyncio as redis
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FirestoreService:
    """
    Firestore database service with caching and batch operations support.
    """
    
    def __init__(self):
        self.db: Optional[AsyncClient] = None
        self.redis_client: Optional[redis.Redis] = None
        self._connection_pool = {}
    
    async def initialize(self):
        """Initialize Firestore and Redis connections."""
        try:
            # Initialize Firestore with explicit credentials
            credentials = None
            if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                logger.info(f"Loading service account credentials from: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            
            self.db = firestore.AsyncClient(
                project=settings.GCP_PROJECT_ID,
                database=settings.FIRESTORE_DATABASE_ID,
                credentials=credentials
            )
            
            # Initialize Redis for caching
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connections
            await self._test_connections()
            
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {str(e)}")
            raise
    
    async def _test_connections(self):
        """Test database connections."""
        # Test Firestore
        try:
            collections = self.db.collections()
            await collections.__anext__()  # Test async iterator
        except Exception as e:
            logger.warning(f"Firestore connection test failed: {str(e)}")
        
        # Test Redis
        try:
            await self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection test failed: {str(e)}")
    
    async def batch_write_operations(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Perform batch write operations for better performance.
        
        Args:
            operations: List of operations with type, collection, doc_id, and data
            
        Returns:
            bool: Success status of batch operation
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        batch = self.db.batch()
        
        try:
            for operation in operations:
                doc_ref = self.db.collection(operation['collection']).document(operation['doc_id'])
                
                if operation['type'] == 'set':
                    batch.set(doc_ref, operation['data'])
                elif operation['type'] == 'update':
                    batch.update(doc_ref, operation['data'])
                elif operation['type'] == 'delete':
                    batch.delete(doc_ref)
            
            await batch.commit()
            logger.info(f"Batch operation completed successfully: {len(operations)} operations")
            return True
            
        except Exception as e:
            logger.error(f"Batch write operation failed: {str(e)}")
            return False
    
    async def get_with_cache(
        self, 
        collection: str, 
        doc_id: str, 
        cache_ttl: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Get document with Redis caching.
        
        Args:
            collection: Firestore collection name
            doc_id: Document ID
            cache_ttl: Cache TTL in seconds
            
        Returns:
            Document data or None if not found
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cache_key = f"{collection}:{doc_id}"
        
        # Try to get from cache first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache read failed: {str(e)}")
        
        # Get from Firestore
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = await doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            
            # Cache the result
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        cache_key, 
                        cache_ttl, 
                        json.dumps(data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Cache write failed: {str(e)}")
            
            return data
        
        return None
    
    async def paginated_query(
        self, 
        collection: str, 
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: int = 20,
        start_after: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Perform paginated queries efficiently.
        
        Args:
            collection: Collection name
            filters: List of (field, operator, value) tuples
            order_by: Field to order by
            limit: Maximum results per page
            start_after: Document to start after (for pagination)
            
        Returns:
            Dictionary with results, has_more flag, and pagination info
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        query = self.db.collection(collection)
        
        # Apply filters
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        # Apply ordering
        if order_by:
            query = query.order_by(order_by)
        
        # Apply pagination
        if start_after:
            query = query.start_after(start_after)
        
        query = query.limit(limit + 1)  # Get one extra to check if more pages exist
        
        docs = query.stream()
        results = []
        
        async for doc in docs:
            results.append({
                'id': doc.id,
                'data': doc.to_dict()
            })
        
        has_more = len(results) > limit
        if has_more:
            results = results[:-1]  # Remove the extra document
        
        return {
            'results': results,
            'has_more': has_more,
            'last_doc': results[-1]['id'] if results else None,
            'total_returned': len(results)
        }
    
    async def invalidate_cache(self, pattern: str = None):
        """
        Invalidate cache entries by pattern.
        
        Args:
            pattern: Redis key pattern to match (e.g., "trips:*")
        """
        if not self.redis_client:
            return
        
        try:
            if pattern:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                await self.redis_client.flushdb()
            
            logger.info(f"Cache invalidated for pattern: {pattern}")
            
        except Exception as e:
            logger.error(f"Cache invalidation failed: {str(e)}")
    
    async def close(self):
        """Close database connections."""
        if self.redis_client:
            await self.redis_client.close()


# Global database service instance
db_service = FirestoreService()


async def initialize_firestore():
    """Initialize the global database service."""
    await db_service.initialize()


async def get_database() -> FirestoreService:
    """
    Get the database service instance.
    
    Returns:
        FirestoreService: Database service instance
    """
    return db_service


# Database dependency for FastAPI
async def get_db() -> FirestoreService:
    """FastAPI dependency for database access."""
    return await get_database()
