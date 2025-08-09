"""
Redis Manager for Splunk MCP Server
Provides caching, session management, rate limiting, and task queue functionality
"""

import redis
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import os

logger = logging.getLogger(__name__)

class RedisManager:
    """Manages Redis connections and operations for the MCP server"""
    
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.password = os.getenv('REDIS_PASSWORD', None)
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self.client is not None
    
    # Session Management
    def store_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store session data with TTL"""
        if not self.is_connected():
            return False
        
        try:
            self.client.setex(
                f"session:{session_id}",
                ttl,
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        if not self.is_connected():
            return None
        
        try:
            data = self.client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        if not self.is_connected():
            return False
        
        try:
            self.client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    # Caching
    def cache_query(self, query: str, result: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache Splunk query results"""
        if not self.is_connected():
            return False
        
        try:
            cache_key = f"cache:query:{hashlib.md5(query.encode()).hexdigest()}"
            self.client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cache query: {e}")
            return False
    
    def get_cached_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached query results"""
        if not self.is_connected():
            return None
        
        try:
            cache_key = f"cache:query:{hashlib.md5(query.encode()).hexdigest()}"
            data = self.client.get(cache_key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get cached query: {e}")
            return None
    
    def cache_itsi_data(self, data_type: str, key: str, data: Dict[str, Any], ttl: int = 60) -> bool:
        """Cache ITSI data (services, kpis, etc.)"""
        if not self.is_connected():
            return False
        
        try:
            cache_key = f"cache:itsi:{data_type}:{key}"
            self.client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cache ITSI data: {e}")
            return False
    
    def get_cached_itsi_data(self, data_type: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached ITSI data"""
        if not self.is_connected():
            return None
        
        try:
            cache_key = f"cache:itsi:{data_type}:{key}"
            data = self.client.get(cache_key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get cached ITSI data: {e}")
            return None
    
    # Rate Limiting
    def check_rate_limit(self, identifier: str, limit: int, window: int = 60) -> tuple[bool, int]:
        """Check rate limit using sliding window"""
        if not self.is_connected():
            return True, limit
        
        try:
            key = f"rate_limit:{identifier}"
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window)
            
            # Remove old entries
            self.client.zremrangebyscore(key, 0, window_start.timestamp())
            
            # Count current entries
            current_count = self.client.zcard(key)
            
            if current_count < limit:
                # Add new entry
                self.client.zadd(key, {str(now.timestamp()): now.timestamp()})
                self.client.expire(key, window)
                return True, limit - current_count - 1
            else:
                return False, 0
                
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True, limit
    
    # Task Queue
    def enqueue_task(self, task_type: str, task_data: Dict[str, Any], priority: int = 0) -> Optional[str]:
        """Add task to Redis queue"""
        if not self.is_connected():
            return None
        
        try:
            task_id = f"task:{task_type}:{datetime.utcnow().isoformat()}"
            task = {
                "id": task_id,
                "type": task_type,
                "data": task_data,
                "priority": priority,
                "created": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            self.client.lpush(f"queue:{task_type}", json.dumps(task))
            return task_id
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            return None
    
    def get_task(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get task from Redis queue"""
        if not self.is_connected():
            return None
        
        try:
            task_data = self.client.brpop(f"queue:{task_type}", timeout=1)
            if task_data:
                return json.loads(task_data[1])
            return None
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None
    
    def update_task_status(self, task_id: str, status: str, result: Any = None) -> bool:
        """Update task status and result"""
        if not self.is_connected():
            return False
        
        try:
            task_key = f"task:{task_id}"
            self.client.hset(task_key, mapping={
                "status": status,
                "result": json.dumps(result) if result else None,
                "updated": datetime.utcnow().isoformat()
            })
            self.client.expire(task_key, 3600)  # Keep for 1 hour
            return True
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result"""
        if not self.is_connected():
            return None
        
        try:
            task_key = f"task:{task_id}"
            data = self.client.hgetall(task_key)
            return dict(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return None
    
    # Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check Redis health and statistics"""
        if not self.is_connected():
            return {"status": "disconnected", "error": "Not connected"}
        
        try:
            info = self.client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_days": info.get("uptime_in_days"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses")
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global Redis manager instance
redis_manager = RedisManager()