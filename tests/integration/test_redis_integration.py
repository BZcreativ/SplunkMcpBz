#!/usr/bin/env python3
"""
Test script for Redis integration in Splunk MCP Server
Tests all Redis functionality including caching, rate limiting, and health checks
"""

import asyncio
import sys
import os
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from splunk_mcp.redis_manager import redis_manager

def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("Testing Redis connection...")
    
    if not redis_manager.is_connected():
        print("❌ Redis is not connected")
        return False
    
    print("✅ Redis connection successful")
    
    # Test health check
    health = redis_manager.health_check()
    print(f"Redis Health: {health}")
    
    return True

def test_caching():
    """Test Redis caching functionality"""
    print("\nTesting Redis caching...")
    
    # Test query caching
    test_query = "search index=_internal | head 10"
    test_result = {"results": [{"test": "data"}], "count": 1}
    
    # Cache the query
    success = redis_manager.cache_query(test_query, test_result, ttl=10)
    if not success:
        print("❌ Failed to cache query")
        return False
    
    print("✅ Query caching successful")
    
    # Retrieve cached query
    cached = redis_manager.get_cached_query(test_query)
    if not cached or cached != test_result:
        print("❌ Failed to retrieve cached query")
        return False
    
    print("✅ Cached query retrieval successful")
    
    # Test ITSI caching
    itsi_data = {"services": [{"name": "test_service"}]}
    success = redis_manager.cache_itsi_data("services", "test_key", itsi_data, ttl=10)
    if not success:
        print("❌ Failed to cache ITSI data")
        return False
    
    print("✅ ITSI caching successful")
    
    return True

def test_rate_limiting():
    """Test Redis rate limiting"""
    print("\nTesting Redis rate limiting...")
    
    test_user = "test_user"
    limit = 5
    
    # Test within limit
    for i in range(limit):
        allowed, remaining = redis_manager.check_rate_limit(test_user, limit, window=60)
        if not allowed:
            print(f"❌ Rate limit failed on iteration {i}")
            return False
    
    print("✅ Rate limiting within limit successful")
    
    # Test exceeding limit
    allowed, remaining = redis_manager.check_rate_limit(test_user, limit, window=60)
    if allowed:
        print("❌ Rate limit should have blocked")
        return False
    
    print("✅ Rate limiting blocking successful")
    
    return True

def test_sessions():
    """Test Redis session management"""
    print("\nTesting Redis session management...")
    
    session_id = "test_session_123"
    session_data = {
        "user_id": "test_user",
        "roles": ["user", "test"],
        "created": "2024-01-01T00:00:00"
    }
    
    # Store session
    success = redis_manager.store_session(session_id, session_data, ttl=10)
    if not success:
        print("❌ Failed to store session")
        return False
    
    print("✅ Session storage successful")
    
    # Retrieve session
    retrieved = redis_manager.get_session(session_id)
    if not retrieved or retrieved != session_data:
        print("❌ Failed to retrieve session")
        return False
    
    print("✅ Session retrieval successful")
    
    # Delete session
    success = redis_manager.delete_session(session_id)
    if not success:
        print("❌ Failed to delete session")
        return False
    
    print("✅ Session deletion successful")
    
    return True

def test_task_queue():
    """Test Redis task queue functionality"""
    print("\nTesting Redis task queue...")
    
    task_type = "splunk_search"
    task_data = {"query": "search index=_internal", "user": "test_user"}
    
    # Enqueue task
    task_id = redis_manager.enqueue_task(task_type, task_data, priority=1)
    if not task_id:
        print("❌ Failed to enqueue task")
        return False
    
    print(f"✅ Task enqueued with ID: {task_id}")
    
    # Update task status
    success = redis_manager.update_task_status(task_id, "processing")
    if not success:
        print("❌ Failed to update task status")
        return False
    
    print("✅ Task status update successful")
    
    # Get task status
    status = redis_manager.get_task_status(task_id)
    if not status:
        print("❌ Failed to get task status")
        return False
    
    print(f"✅ Task status retrieval: {status}")
    
    return True

async def run_all_tests():
    """Run all Redis integration tests"""
    print("🚀 Starting Redis Integration Tests\n")
    
    tests = [
        test_redis_connection,
        test_caching,
        test_rate_limiting,
        test_sessions,
        test_task_queue
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Redis integration tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)