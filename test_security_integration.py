#!/usr/bin/env python3
"""
Security Integration Test Script for Splunk MCP Server
Tests authentication, authorization, and security features
"""

import requests
import json
import time
from typing import Dict, Any

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8334"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def test_health_endpoint(self) -> bool:
        """Test health endpoint (public)"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_login(self, username: str, password: str) -> bool:
        """Test login endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print(f"✅ Login successful for {username}: {data['roles']}")
                return True
            else:
                print(f"❌ Login failed for {username}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_invalid_login(self) -> bool:
        """Test invalid login"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "invalid", "password": "invalid"}
            )
            if response.status_code == 401:
                print("✅ Invalid login properly rejected")
                return True
            else:
                print(f"❌ Invalid login should be rejected: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Invalid login test error: {e}")
            return False
    
    def test_protected_endpoint(self, endpoint: str, expected_status: int = 200) -> bool:
        """Test protected endpoint with authentication"""
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
            if response.status_code == expected_status:
                print(f"✅ {endpoint} access: {response.status_code}")
                return True
            else:
                print(f"❌ {endpoint} unexpected status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
            return False
    
    def test_unauthorized_endpoint(self, endpoint: str) -> bool:
        """Test endpoint without authentication"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} properly requires auth")
                return True
            else:
                print(f"❌ {endpoint} should require auth: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {endpoint} unauthorized test error: {e}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Make multiple rapid requests
            for i in range(105):  # Exceed default limit
                response = self.session.get(f"{self.base_url}/api/auth/me", headers=headers)
                if response.status_code == 429:
                    print(f"✅ Rate limiting triggered at request {i+1}")
                    return True
            print("❌ Rate limiting not triggered")
            return False
        except Exception as e:
            print(f"❌ Rate limiting test error: {e}")
            return False
    
    def test_user_info(self) -> bool:
        """Test user info endpoint"""
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{self.base_url}/api/auth/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User info: {data}")
                return True
            else:
                print(f"❌ User info failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User info error: {e}")
            return False
    
    def test_token_refresh(self) -> bool:
        """Test token refresh"""
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.post(
                f"{self.base_url}/api/auth/refresh",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token refresh successful")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return False
    
    def test_mcp_tools_with_auth(self) -> bool:
        """Test MCP tools with authentication"""
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Test MCP health check
            response = self.session.get(f"{self.base_url}/mcp/mcp_health_check", headers=headers)
            if response.status_code == 200:
                print("✅ MCP tools accessible with auth")
                return True
            else:
                print(f"❌ MCP tools access failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP tools test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔐 Starting Security Integration Tests\n")
        
        # Test 1: Health endpoint (public)
        print("1. Testing health endpoint...")
        self.test_health_endpoint()
        
        # Test 2: Invalid login
        print("\n2. Testing invalid login...")
        self.test_invalid_login()
        
        # Test 3: Valid login
        print("\n3. Testing admin login...")
        admin_login = self.test_login("admin", "admin123")
        
        if admin_login:
            # Test 4: User info
            print("\n4. Testing user info...")
            self.test_user_info()
            
            # Test 5: Protected endpoints
            print("\n5. Testing protected endpoints...")
            self.test_protected_endpoint("/api/metrics")
            self.test_protected_endpoint("/api/test-splunk-connection")
            
            # Test 6: MCP tools
            print("\n6. Testing MCP tools...")
            self.test_mcp_tools_with_auth()
            
            # Test 7: Token refresh
            print("\n7. Testing token refresh...")
            self.test_token_refresh()
        
        # Test 8: User login
        print("\n8. Testing user login...")
        self.session = requests.Session()  # Reset session
        user_login = self.test_login("user", "user123")
        
        if user_login:
            print("\n9. Testing user permissions...")
            self.test_protected_endpoint("/api/metrics", expected_status=403)
        
        # Test 10: Readonly login
        print("\n10. Testing readonly login...")
        self.session = requests.Session()  # Reset session
        readonly_login = self.test_login("readonly", "readonly123")
        
        if readonly_login:
            print("\n11. Testing readonly permissions...")
            self.test_protected_endpoint("/api/metrics", expected_status=403)
        
        print("\n✅ Security integration tests completed!")

def main():
    """Main test runner"""
    tester = SecurityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
