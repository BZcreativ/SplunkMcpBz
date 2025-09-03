
"""
Redis Cluster Configuration for High Availability
Provides Redis clustering and sentinel support for production deployments
"""

import os
import redis
from typing import List, Dict, Any, Optional
from redis.sentinel import Sentinel
from redis.cluster import RedisCluster
import logging

logger = logging.getLogger(__name__)

class RedisClusterConfig:
    """Redis clustering configuration"""
    
    def __init__(self):
        self.cluster_mode = os.getenv("REDIS_CLUSTER_MODE", "single").lower()
        self.sentinel_hosts = self._parse_sentinel_hosts()
        self.cluster_nodes = self._parse_cluster_nodes()
        self.master_name = os.getenv("REDIS_MASTER_NAME", "mymaster")
        self.password = os.getenv("REDIS_PASSWORD")
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.socket_timeout = float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0"))
        self.socket_connect_timeout = float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0"))
        
    def _parse_sentinel_hosts(self) -> List[tuple]:
        """Parse Redis Sentinel hosts from environment"""
        sentinel_str = os.getenv("REDIS_SENTINEL_HOSTS", "")
        if not sentinel_str:
            return []
        
        hosts = []
        for host_port in sentinel_str.split(","):
            host, port = host_port.strip().split(":")
            hosts.append((host, int(port)))
        return hosts
    
    def _parse_cluster_nodes(self) -> List[Dict[str, Any]]:
        """Parse Redis Cluster nodes from environment"""
        cluster_str = os.getenv("REDIS_CLUSTER_NODES", "")
        if not cluster_str:
            return []
        
        nodes = []
        for node_str in cluster_str.split(","):
            host, port = node_str.strip().split(":")
            nodes.append({"host": host, "port": int(port)})
        return nodes
    
    def create_redis_client(self) -> redis.Redis:
        """Create appropriate Redis client based on configuration"""
        
        if self.cluster_mode == "sentinel" and self.sentinel_hosts:
            return self._create_sentinel_client()
        elif self.cluster_mode == "cluster" and self.cluster_nodes:
            return self._create_cluster_client()
        else:
            return self._create_single_client()
    
    def _create_sentinel_client(self) -> redis.Redis:
        """Create Redis Sentinel client"""
        if not self.sentinel_hosts:
            raise ValueError("Redis Sentinel hosts not configured")
        
        sentinel = Sentinel(
            self.sentinel_hosts,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            password=self.password,
            db=self.db
        )
        
        return sentinel.master_for(
            self.master_name,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout
        )
    
    def _create_cluster_client(self) -> redis.Redis:
        """Create Redis Cluster client"""
        if not self.cluster_nodes:
            raise ValueError("Redis Cluster nodes not configured")
        
        startup_nodes = [
            {"host": node["host"], "port": node["port"]}
            for node in self.cluster_nodes
        ]
        
        return RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            password=self.password
        )
    
    def _create_single_client(self) -> redis.Redis:
        """Create single Redis client"""
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=self.db,
            password=self.password,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            decode_responses=True
        )

class RedisHealthChecker:
    """Redis health checking utilities"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def check_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            # Test basic connectivity
            self.redis_client.ping()
            
            # Get Redis info
            info = self.redis_client.info()
            
            return {
                "status": "healthy",
                "connected": True,
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "cluster_mode": self.cluster_mode
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }

# Example Docker Compose for Redis Cluster
DOCKER_COMPOSE_REDIS_CLUSTER = """
version: '3.
