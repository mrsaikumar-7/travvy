#!/usr/bin/env python3
"""
GCP Connection Tests

This script tests all Google Cloud Platform service connections
to verify that environment variables and credentials are properly configured.
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import FirestoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GCPConnectionTester:
    """Test all GCP service connections."""
    
    def __init__(self):
        self.settings = get_settings()
        self.results = {}
        
    async def test_firestore_connection(self) -> Dict[str, Any]:
        """Test Firestore database connection."""
        logger.info("🔍 Testing Firestore connection...")
        
        try:
            # Initialize Firestore service
            firestore_service = FirestoreService()
            await firestore_service.initialize()
            
            # Test basic operations
            test_collection = f"{self.settings.FIRESTORE_COLLECTION_PREFIX}test_connection"
            test_doc_id = f"test_{int(datetime.now().timestamp())}"
            test_data = {
                "test_field": "test_value",
                "timestamp": datetime.now(),
                "connection_test": True
            }
            
            # Test write operation
            doc_ref = firestore_service.db.collection(test_collection).document(test_doc_id)
            await doc_ref.set(test_data)
            
            # Test read operation
            doc = await doc_ref.get()
            if doc.exists:
                retrieved_data = doc.to_dict()
                logger.info(f"✅ Retrieved test document: {retrieved_data}")
            
            # Test with cache
            cached_data = await firestore_service.get_with_cache(
                test_collection, test_doc_id, cache_ttl=10
            )
            
            # Clean up test document
            await doc_ref.delete()
            
            await firestore_service.close()
            
            return {
                "service": "Firestore",
                "status": "✅ CONNECTED",
                "project_id": self.settings.GCP_PROJECT_ID,
                "database_id": self.settings.FIRESTORE_DATABASE_ID,
                "test_operations": "READ/WRITE/CACHE - SUCCESS",
                "details": {
                    "write_success": True,
                    "read_success": doc.exists if doc else False,
                    "cache_success": cached_data is not None,
                    "test_doc_id": test_doc_id
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Firestore connection failed: {str(e)}")
            return {
                "service": "Firestore",
                "status": "❌ FAILED",
                "error": str(e),
                "project_id": self.settings.GCP_PROJECT_ID,
                "database_id": self.settings.FIRESTORE_DATABASE_ID
            }
    
    async def test_google_ai_connection(self) -> Dict[str, Any]:
        """Test Google Generative AI (Gemini) connection."""
        logger.info("🔍 Testing Google AI (Gemini) connection...")
        
        try:
            import google.generativeai as genai
            
            # Configure the API key
            genai.configure(api_key=self.settings.GOOGLE_AI_API_KEY)
            
            # Test with a simple prompt
            model = genai.GenerativeModel(self.settings.AI_MODEL_NAME)
            
            test_prompt = "Hello! This is a connection test. Please respond with 'Connection successful'."
            
            response = await asyncio.to_thread(
                model.generate_content, 
                test_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.settings.AI_TEMPERATURE,
                    max_output_tokens=50
                )
            )
            
            response_text = response.text if response else "No response"
            
            return {
                "service": "Google AI (Gemini)",
                "status": "✅ CONNECTED",
                "model": self.settings.AI_MODEL_NAME,
                "test_prompt": test_prompt,
                "response": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                "details": {
                    "temperature": self.settings.AI_TEMPERATURE,
                    "max_tokens": self.settings.AI_MAX_OUTPUT_TOKENS,
                    "response_length": len(response_text)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Google AI connection failed: {str(e)}")
            return {
                "service": "Google AI (Gemini)",
                "status": "❌ FAILED",
                "error": str(e),
                "model": self.settings.AI_MODEL_NAME,
                "api_key_configured": bool(self.settings.GOOGLE_AI_API_KEY)
            }
    
    async def test_google_auth_connection(self) -> Dict[str, Any]:
        """Test Google OAuth connection."""
        logger.info("🔍 Testing Google OAuth configuration...")
        
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            import google.auth
            
            # Test if credentials are properly configured
            credentials = None
            project_id = None
            
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(self.settings.GOOGLE_APPLICATION_CREDENTIALS):
                # Test service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                project_id = credentials.project_id
                logger.info(f"✅ Service account credentials loaded from: {self.settings.GOOGLE_APPLICATION_CREDENTIALS}")
            else:
                # Try default credentials
                credentials, project_id = google.auth.default()
                logger.info("✅ Default credentials found")
            
            # Test OAuth client configuration
            oauth_configured = bool(self.settings.GOOGLE_CLIENT_ID and self.settings.GOOGLE_CLIENT_SECRET)
            
            return {
                "service": "Google Auth",
                "status": "✅ CONFIGURED",
                "project_id": project_id,
                "service_account_file": self.settings.GOOGLE_APPLICATION_CREDENTIALS,
                "service_account_valid": credentials is not None,
                "oauth_client_configured": oauth_configured,
                "details": {
                    "client_id": self.settings.GOOGLE_CLIENT_ID[:20] + "..." if self.settings.GOOGLE_CLIENT_ID else "Not configured",
                    "credentials_type": type(credentials).__name__ if credentials else "None"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Google Auth configuration failed: {str(e)}")
            return {
                "service": "Google Auth",
                "status": "❌ FAILED",
                "error": str(e),
                "service_account_file": self.settings.GOOGLE_APPLICATION_CREDENTIALS,
                "oauth_configured": bool(self.settings.GOOGLE_CLIENT_ID and self.settings.GOOGLE_CLIENT_SECRET)
            }
    
    async def test_google_maps_api(self) -> Dict[str, Any]:
        """Test Google Maps and Places API connection."""
        logger.info("🔍 Testing Google Maps API connection...")
        
        try:
            import httpx
            
            # Test Google Maps Geocoding API
            maps_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
            maps_params = {
                "address": "1600 Amphitheatre Parkway, Mountain View, CA",
                "key": self.settings.GOOGLE_MAPS_API_KEY
            }
            
            async with httpx.AsyncClient() as client:
                maps_response = await client.get(maps_api_url, params=maps_params, timeout=10.0)
                maps_data = maps_response.json()
                
                # Test Google Places API
                places_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                places_params = {
                    "input": "Googleplex",
                    "inputtype": "textquery",
                    "fields": "place_id,name",
                    "key": self.settings.GOOGLE_PLACES_API_KEY
                }
                
                places_response = await client.get(places_api_url, params=places_params, timeout=10.0)
                places_data = places_response.json()
            
            maps_success = maps_data.get("status") == "OK"
            places_success = places_data.get("status") == "OK"
            
            return {
                "service": "Google Maps & Places API",
                "status": "✅ CONNECTED" if maps_success and places_success else "⚠️  PARTIAL",
                "maps_api": {
                    "status": "✅ OK" if maps_success else f"❌ {maps_data.get('status', 'UNKNOWN')}",
                    "results_count": len(maps_data.get("results", []))
                },
                "places_api": {
                    "status": "✅ OK" if places_success else f"❌ {places_data.get('status', 'UNKNOWN')}",
                    "candidates_count": len(places_data.get("candidates", []))
                },
                "details": {
                    "maps_api_configured": bool(self.settings.GOOGLE_MAPS_API_KEY),
                    "places_api_configured": bool(self.settings.GOOGLE_PLACES_API_KEY)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Google Maps API connection failed: {str(e)}")
            return {
                "service": "Google Maps & Places API",
                "status": "❌ FAILED",
                "error": str(e),
                "maps_api_configured": bool(self.settings.GOOGLE_MAPS_API_KEY),
                "places_api_configured": bool(self.settings.GOOGLE_PLACES_API_KEY)
            }
    
    async def test_redis_connection(self) -> Dict[str, Any]:
        """Test Redis connection (used for caching)."""
        logger.info("🔍 Testing Redis connection...")
        
        try:
            import redis.asyncio as redis
            
            redis_client = redis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test basic operations
            test_key = f"test_connection_{int(datetime.now().timestamp())}"
            test_value = "connection_test_value"
            
            # Test write
            await redis_client.set(test_key, test_value, ex=10)  # 10 second expiry
            
            # Test read
            retrieved_value = await redis_client.get(test_key)
            
            # Test delete
            await redis_client.delete(test_key)
            
            # Get info
            info = await redis_client.info()
            
            await redis_client.close()
            
            return {
                "service": "Redis Cache",
                "status": "✅ CONNECTED",
                "redis_url": self.settings.REDIS_URL,
                "test_operations": "SET/GET/DELETE - SUCCESS",
                "details": {
                    "write_success": True,
                    "read_success": retrieved_value == test_value,
                    "redis_version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            return {
                "service": "Redis Cache",
                "status": "❌ FAILED",
                "error": str(e),
                "redis_url": self.settings.REDIS_URL
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all GCP connection tests."""
        logger.info("🚀 Starting GCP connection tests...")
        
        start_time = datetime.now()
        
        # Run all tests concurrently
        tests = await asyncio.gather(
            self.test_firestore_connection(),
            self.test_google_ai_connection(),
            self.test_google_auth_connection(),
            self.test_google_maps_api(),
            self.test_redis_connection(),
            return_exceptions=True
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Compile results
        results = {
            "test_summary": {
                "total_tests": len(tests),
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "environment": self.settings.ENVIRONMENT,
                "project_id": self.settings.GCP_PROJECT_ID
            },
            "test_results": {}
        }
        
        success_count = 0
        for test_result in tests:
            if isinstance(test_result, Exception):
                logger.error(f"Test failed with exception: {test_result}")
                continue
                
            service_name = test_result.get("service", "Unknown")
            results["test_results"][service_name] = test_result
            
            if "✅" in test_result.get("status", ""):
                success_count += 1
        
        results["test_summary"]["successful_tests"] = success_count
        results["test_summary"]["failed_tests"] = len(tests) - success_count
        results["test_summary"]["success_rate"] = f"{(success_count/len(tests)*100):.1f}%"
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Pretty print test results."""
        print("\n" + "="*60)
        print("🧪 GCP CONNECTION TEST RESULTS")
        print("="*60)
        
        summary = results["test_summary"]
        print(f"📊 Summary:")
        print(f"   • Total Tests: {summary['total_tests']}")
        print(f"   • Success Rate: {summary['success_rate']}")
        print(f"   • Duration: {summary['duration_seconds']:.2f}s")
        print(f"   • Environment: {summary['environment']}")
        print(f"   • Project ID: {summary['project_id']}")
        print()
        
        print("🔍 Detailed Results:")
        for service, result in results["test_results"].items():
            print(f"\n   {service}:")
            print(f"     Status: {result['status']}")
            
            if "error" in result:
                print(f"     Error: {result['error']}")
            
            if "details" in result:
                print(f"     Details: {json.dumps(result['details'], indent=6, default=str)}")
        
        print("\n" + "="*60)


async def main():
    """Main test runner."""
    try:
        tester = GCPConnectionTester()
        results = await tester.run_all_tests()
        tester.print_results(results)
        
        # Save results to file
        output_file = f"/tmp/gcp_test_results_{int(datetime.now().timestamp())}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Return exit code based on success rate
        success_rate = float(results["test_summary"]["success_rate"].rstrip('%'))
        exit_code = 0 if success_rate >= 80 else 1
        
        print(f"\n🎯 Exit code: {exit_code} (0=success, 1=failure)")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Test runner failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
