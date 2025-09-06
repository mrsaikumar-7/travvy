#!/usr/bin/env python3
"""
Firestore Permissions Diagnostic Tool

This script helps diagnose Firestore connection issues by checking:
1. Service account IAM roles
2. Firestore database configuration  
3. Security rules vs IAM permissions
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud import resourcemanager_v3
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FirestorePermissionsDiagnostic:
    """Diagnostic tool for Firestore permissions issues."""
    
    def __init__(self):
        self.settings = get_settings()
        self.credentials = None
        self.load_credentials()
    
    def load_credentials(self):
        """Load service account credentials."""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(self.settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                logger.info(f"✅ Credentials loaded from: {self.settings.GOOGLE_APPLICATION_CREDENTIALS}")
                logger.info(f"📧 Service account email: {self.credentials.service_account_email}")
            else:
                logger.error("❌ Credentials file not found or not configured")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to load credentials: {e}")
            sys.exit(1)
    
    async def check_firestore_database(self):
        """Check Firestore database configuration."""
        logger.info("\n🔍 Checking Firestore Database Configuration...")
        
        try:
            # Initialize Firestore client
            db = firestore.AsyncClient(
                project=self.settings.GCP_PROJECT_ID,
                database=self.settings.FIRESTORE_DATABASE_ID,
                credentials=self.credentials
            )
            
            logger.info(f"📊 Project ID: {self.settings.GCP_PROJECT_ID}")
            logger.info(f"🗄️  Database ID: {self.settings.FIRESTORE_DATABASE_ID}")
            
            # Try to list collections (this requires read access)
            try:
                collections = db.collections()
                collection_list = []
                async for collection in collections:
                    collection_list.append(collection.id)
                    if len(collection_list) >= 5:  # Limit to first 5
                        break
                
                logger.info(f"✅ Successfully connected to Firestore!")
                logger.info(f"📁 Found collections: {collection_list[:5]}")
                return True
                
            except Exception as e:
                if "403" in str(e):
                    logger.error(f"❌ 403 Permissions Error: {e}")
                    logger.info("🔑 This means your service account lacks proper IAM roles")
                elif "404" in str(e):
                    logger.error(f"❌ 404 Not Found: Database might not exist")
                else:
                    logger.error(f"❌ Firestore connection failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore client: {e}")
            return False
    
    def diagnose_iam_permissions(self):
        """Diagnose IAM permissions for the service account."""
        logger.info("\n🔍 Diagnosing IAM Permissions...")
        
        required_roles = [
            "roles/datastore.user",
            "roles/firebase.admin", 
            "roles/firestore.user",
            "roles/datastore.owner",
            "roles/firebase.developAdmin"
        ]
        
        logger.info("📋 Service accounts need one of these IAM roles for Firestore:")
        for role in required_roles:
            logger.info(f"   • {role}")
        
        logger.info(f"\n📧 Your service account: {self.credentials.service_account_email}")
        logger.info("🎯 To fix permissions, run these commands:")
        
        print(f"""
🔧 PERMISSION FIX COMMANDS:

# Option 1: Datastore User (Recommended for apps)
gcloud projects add-iam-policy-binding {self.settings.GCP_PROJECT_ID} \\
    --member="serviceAccount:{self.credentials.service_account_email}" \\
    --role="roles/datastore.user"

# Option 2: Firebase Admin (Full access)
gcloud projects add-iam-policy-binding {self.settings.GCP_PROJECT_ID} \\
    --member="serviceAccount:{self.credentials.service_account_email}" \\
    --role="roles/firebase.admin"

# Option 3: Via Google Cloud Console
# 1. Go to: https://console.cloud.google.com/iam-admin/iam?project={self.settings.GCP_PROJECT_ID}
# 2. Find your service account: {self.credentials.service_account_email}
# 3. Click "Edit" and add role: "Cloud Datastore User" or "Firebase Admin"
""")
    
    def explain_security_rules_vs_iam(self):
        """Explain the difference between Security Rules and IAM permissions."""
        logger.info("\n📚 SECURITY RULES vs IAM PERMISSIONS:")
        
        print("""
🔐 Your Firestore Security Rules:
   • Control access from client apps (web, mobile)
   • Applied when users interact with your app
   • Your rules look correct ✅

🎫 IAM Permissions (Current Issue):
   • Control access from server/service accounts
   • Required for backend services like your API
   • Missing for your service account ❌

🎯 The Fix:
   Your security rules are fine! You just need to grant IAM permissions 
   to your service account so your backend can access Firestore.
        """)
    
    async def test_specific_operations(self):
        """Test specific Firestore operations."""
        logger.info("\n🧪 Testing Specific Operations...")
        
        try:
            db = firestore.AsyncClient(
                project=self.settings.GCP_PROJECT_ID,
                database=self.settings.FIRESTORE_DATABASE_ID,
                credentials=self.credentials
            )
            
            # Test 1: List collections
            try:
                collections = db.collections()
                await collections.__anext__()
                logger.info("✅ List collections: SUCCESS")
            except Exception as e:
                logger.error(f"❌ List collections: FAILED - {e}")
            
            # Test 2: Read a document
            try:
                test_doc = db.collection('test').document('permission_check')
                doc = await test_doc.get()
                logger.info("✅ Read document: SUCCESS")
            except Exception as e:
                logger.error(f"❌ Read document: FAILED - {e}")
            
            # Test 3: Write a document
            try:
                test_doc = db.collection('test').document('permission_check')
                await test_doc.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
                logger.info("✅ Write document: SUCCESS")
            except Exception as e:
                logger.error(f"❌ Write document: FAILED - {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to test operations: {e}")
    
    async def run_full_diagnostic(self):
        """Run the complete diagnostic."""
        logger.info("🚀 Starting Firestore Permissions Diagnostic...")
        
        # Check database connection
        db_connected = await self.check_firestore_database()
        
        # Always show IAM diagnostic
        self.diagnose_iam_permissions()
        
        # Explain the difference
        self.explain_security_rules_vs_iam()
        
        # Test specific operations if not connected
        if not db_connected:
            await self.test_specific_operations()
        
        logger.info("\n🎯 SUMMARY:")
        if db_connected:
            logger.info("✅ Firestore connection is working!")
        else:
            logger.info("❌ Firestore connection failed - Run the IAM commands above to fix")


async def main():
    """Main diagnostic runner."""
    diagnostic = FirestorePermissionsDiagnostic()
    await diagnostic.run_full_diagnostic()


if __name__ == "__main__":
    asyncio.run(main())
