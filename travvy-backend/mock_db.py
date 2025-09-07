#!/usr/bin/env python3
"""
Mock database service for testing without Firestore
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class MockFirestoreService:
    """Mock Firestore service for testing"""
    
    def __init__(self):
        self.data = {}  # In-memory storage
        self.cache = {}
    
    @property 
    def db(self):
        return self
    
    def collection(self, name: str):
        if name not in self.data:
            self.data[name] = {}
        return MockCollection(self.data[name], name)
    
    async def get_with_cache(self, collection: str, doc_id: str, cache_ttl: int = 300):
        """Get document with caching"""
        collection_data = self.data.get(collection, {})
        return collection_data.get(doc_id)
    
    async def invalidate_cache(self, cache_key: str):
        """Invalidate cache"""
        if cache_key in self.cache:
            del self.cache[cache_key]
    
    async def paginated_query(self, collection: str, filters: List = None, 
                             order_by: str = None, limit: int = 20, start_after = None):
        """Mock paginated query"""
        collection_data = self.data.get(collection, {})
        results = []
        
        for doc_id, doc_data in collection_data.items():
            # Simple filtering (just for demo)
            matches = True
            if filters:
                for field, op, value in filters:
                    doc_value = doc_data
                    for key in field.split('.'):
                        doc_value = doc_value.get(key) if isinstance(doc_value, dict) else None
                    
                    if op == '==' and doc_value != value:
                        matches = False
                        break
            
            if matches:
                results.append({"id": doc_id, "data": doc_data})
        
        # Simple pagination
        results = results[:limit]
        
        return {
            "results": results,
            "has_more": len(results) >= limit
        }


class MockCollection:
    """Mock Firestore collection"""
    
    def __init__(self, data: Dict, name: str):
        self.data = data
        self.name = name
    
    def document(self, doc_id: str):
        return MockDocument(self.data, doc_id)
    
    def where(self, field: str, op: str, value: Any):
        # Mock where clause
        return self


class MockDocument:
    """Mock Firestore document"""
    
    def __init__(self, collection_data: Dict, doc_id: str):
        self.collection_data = collection_data
        self.doc_id = doc_id
    
    async def set(self, data: Dict[str, Any]):
        """Set document data"""
        # Convert datetime objects to ISO strings for JSON serialization
        serialized_data = self._serialize_data(data)
        self.collection_data[self.doc_id] = serialized_data
        
    async def update(self, updates: Dict[str, Any]):
        """Update document data"""
        if self.doc_id in self.collection_data:
            serialized_updates = self._serialize_data(updates)
            self.collection_data[self.doc_id].update(serialized_updates)
        else:
            raise Exception("Document not found")
    
    async def get(self):
        """Get document data"""
        data = self.collection_data.get(self.doc_id)
        if data:
            return MockDocumentSnapshot(data, self.doc_id)
        return None
    
    def _serialize_data(self, data: Any) -> Any:
        """Convert data to JSON-serializable format"""
        if isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data


class MockDocumentSnapshot:
    """Mock document snapshot"""
    
    def __init__(self, data: Dict, doc_id: str):
        self.data = data
        self.id = doc_id
    
    def exists(self):
        return self.data is not None
    
    def to_dict(self):
        return self.data


# Global mock instance
_mock_db = MockFirestoreService()

async def get_mock_database():
    """Get mock database instance"""
    return _mock_db
