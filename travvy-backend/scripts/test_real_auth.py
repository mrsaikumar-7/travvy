#!/usr/bin/env python3
"""
Test Real Authentication System

This script tests the actual authentication endpoints to ensure they work properly
after switching from the mock implementation.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AuthTester:
    """Test the real authentication system."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_registration(self, email="testuser@example.com", password="testpass123", display_name="Test User"):
        """Test user registration with real API."""
        logger.info(f"🧪 Testing registration for: {email}")
        
        try:
            registration_data = {
                "email": email,
                "password": password,
                "display_name": display_name,
                "profile": {
                    "firstName": "Test",
                    "lastName": "User"
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    logger.info("✅ Registration successful!")
                    
                    # Check if we got real tokens or mock tokens
                    access_token = data.get("access_token", "")
                    
                    if access_token.startswith("mock-"):
                        logger.warning("⚠️  Still getting MOCK tokens - check if real API is running")
                        return {
                            "success": False,
                            "error": "Still using mock API",
                            "data": data
                        }
                    else:
                        logger.info("🎯 Got REAL JWT tokens!")
                        logger.info(f"   Access Token (first 20 chars): {access_token[:20]}...")
                        logger.info(f"   User ID: {data.get('user', {}).get('uid', 'N/A')}")
                        
                        return {
                            "success": True,
                            "data": data,
                            "tokens": {
                                "access_token": access_token,
                                "refresh_token": data.get("refresh_token")
                            }
                        }
                
                else:
                    logger.error(f"❌ Registration failed: {response.status}")
                    logger.error(f"   Response: {response_text}")
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response_text}",
                        "data": None
                    }
        
        except Exception as e:
            logger.error(f"❌ Registration test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def test_login(self, email="testuser@example.com", password="testpass123"):
        """Test user login."""
        logger.info(f"🧪 Testing login for: {email}")
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    logger.info("✅ Login successful!")
                    return {"success": True, "data": data}
                else:
                    logger.error(f"❌ Login failed: {response.status}")
                    return {"success": False, "error": response_text}
        
        except Exception as e:
            logger.error(f"❌ Login test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_protected_endpoint(self, access_token):
        """Test accessing protected endpoint with token."""
        logger.info("🧪 Testing protected endpoint access...")
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    logger.info("✅ Protected endpoint access successful!")
                    return {"success": True, "data": json.loads(response_text)}
                else:
                    logger.error(f"❌ Protected endpoint failed: {response.status}")
                    return {"success": False, "error": response_text}
        
        except Exception as e:
            logger.error(f"❌ Protected endpoint test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_health_check(self):
        """Test if the API is responding."""
        logger.info("🧪 Testing API health...")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ API is healthy!")
                    return {"success": True, "data": data}
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_full_test(self):
        """Run complete authentication test suite."""
        logger.info("🚀 Starting Full Authentication Test Suite")
        logger.info("="*50)
        
        # Test unique email to avoid conflicts
        test_email = f"test.{int(datetime.now().timestamp())}@example.com"
        test_password = "SecureTestPass123!"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. Health Check
        health_result = await self.test_health_check()
        results["tests"]["health"] = health_result
        
        if not health_result["success"]:
            logger.error("❌ API is not responding - check if Docker container is running")
            return results
        
        # 2. Registration Test
        reg_result = await self.test_registration(test_email, test_password)
        results["tests"]["registration"] = reg_result
        
        if not reg_result["success"]:
            logger.error("❌ Registration failed - check logs for details")
            if "Still using mock API" in reg_result.get("error", ""):
                logger.info("💡 Tip: The Docker container might still be running the mock API")
                logger.info("   Try: docker-compose restart")
            return results
        
        access_token = reg_result["tokens"]["access_token"]
        
        # 3. Protected Endpoint Test
        protected_result = await self.test_protected_endpoint(access_token)
        results["tests"]["protected_endpoint"] = protected_result
        
        # 4. Login Test (with same user)
        login_result = await self.test_login(test_email, test_password)
        results["tests"]["login"] = login_result
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*50)
        
        for test_name, result in results["tests"].items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            logger.info(f"{test_name.upper():<20}: {status}")
            
            if not result["success"]:
                logger.info(f"{''.ljust(20)}  Error: {result.get('error', 'Unknown')}")
        
        all_passed = all(result["success"] for result in results["tests"].values())
        
        if all_passed:
            logger.info("\n🎉 ALL TESTS PASSED!")
            logger.info("✅ Real authentication is working properly")
            logger.info("🎯 You can now use the real API instead of mock tokens")
        else:
            logger.info("\n❌ Some tests failed - check the errors above")
            
        return results


async def main():
    """Main test runner."""
    logger.info("🧪 Real Authentication System Tester")
    logger.info("This will test if your real auth endpoints work properly")
    logger.info("-" * 50)
    
    async with AuthTester() as tester:
        results = await tester.run_full_test()
        
        # Save results to file
        with open("/tmp/auth_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n💾 Full results saved to: /tmp/auth_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
