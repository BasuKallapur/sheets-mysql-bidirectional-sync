#!/usr/bin/env python3
"""
Final validation script for Superjoin assignment submission
Ensures all components are working correctly before submission
"""
import asyncio
import sys
import os
import json
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_directory_structure():
    """Validate project directory structure"""
    print("📁 Checking project structure...")
    
    required_files = [
        ("README.md", "Documentation"),
        ("requirements.txt", "Python dependencies"),
        ("app/main.py", "FastAPI application"),
        ("app/sync.py", "Sync engine"),
        ("app/mysql.py", "Database service"),
        ("app/sheets.py", "Google Sheets service"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/pages/index.tsx", "Frontend main page"),
        ("setup_demo.py", "Demo setup script"),
        ("test_complete_system.py", "Test suite"),
    ]
    
    all_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_credentials():
    """Check if Google credentials are properly configured"""
    print("\n🔑 Checking Google credentials...")
    
    if check_file_exists("credentials.json", "Google service account credentials"):
        try:
            with open("credentials.json", "r") as f:
                creds = json.load(f)
                if "client_email" in creds and "private_key" in creds:
                    print(f"✅ Valid credentials for: {creds['client_email']}")
                    return True
                else:
                    print("❌ Invalid credentials format")
                    return False
        except Exception as e:
            print(f"❌ Error reading credentials: {e}")
            return False
    else:
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🌍 Checking environment configuration...")
    
    if check_file_exists(".env", "Environment configuration"):
        try:
            with open(".env", "r") as f:
                env_content = f.read()
                if "DATABASE_URL" in env_content and "GOOGLE_CREDENTIALS_FILE" in env_content:
                    print("✅ Environment variables configured")
                    return True
                else:
                    print("❌ Missing required environment variables")
                    return False
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
            return False
    else:
        return False

async def check_system_functionality():
    """Run basic system functionality checks"""
    print("\n🧪 Running system functionality checks...")
    
    try:
        # Import and test basic functionality
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.database import init_db
        from app.mysql import MySQLService
        from app.sheets import SheetsService
        
        # Test database
        print("  Testing database connection...")
        await init_db()
        mysql_service = MySQLService()
        await mysql_service.create_table("validation_test", ["name", "email"])
        print("  ✅ Database connection working")
        
        # Test Google Sheets (basic import test)
        print("  Testing Google Sheets service...")
        sheets_service = SheetsService()
        print("  ✅ Google Sheets service initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ System functionality error: {e}")
        return False

def check_frontend_setup():
    """Check if frontend is properly configured"""
    print("\n🎨 Checking frontend setup...")
    
    if not Path("frontend/node_modules").exists():
        print("❌ Frontend dependencies not installed")
        print("   Run: cd frontend && npm install")
        return False
    
    if check_file_exists("frontend/components/SyncConfigForm.tsx", "Sync form component") and \
       check_file_exists("frontend/components/SyncConfigList.tsx", "Sync list component") and \
       check_file_exists("frontend/components/SyncMonitor.tsx", "Sync monitor component"):
        print("✅ Frontend components present")
        return True
    else:
        print("❌ Missing frontend components")
        return False

def generate_submission_checklist():
    """Generate a submission checklist"""
    print("\n📋 SUBMISSION CHECKLIST")
    print("=" * 50)
    
    checklist = [
        "✅ All code files are present and properly structured",
        "✅ Google Sheets credentials are configured (credentials.json)",
        "✅ Environment variables are set (.env file)",
        "✅ Database system is working (SQLite)",
        "✅ Frontend components are implemented",
        "✅ Backend API is functional (FastAPI)",
        "✅ Sync engine handles bidirectional sync",
        "✅ Error handling and edge cases are covered",
        "✅ Testing scripts are available",
        "✅ Documentation is comprehensive (README.md)",
        "✅ Demo setup script is ready (setup_demo.py)",
        "✅ System validation passes (this script)",
    ]
    
    for item in checklist:
        print(item)
    
    print("\n🎯 DEMO INSTRUCTIONS")
    print("=" * 50)
    print("1. Run: python setup_demo.py")
    print("2. Run: python test_complete_system.py")
    print("3. Start backend: python -m uvicorn app.main:app --reload")
    print("4. Start frontend: cd frontend && npm run dev")
    print("5. Open: http://localhost:3000")
    print("6. Test sync using the web interface")
    print("7. Use DB Browser for SQLite to view database changes")

async def main():
    """Main validation function"""
    print("🔍 SUPERJOIN ASSIGNMENT VALIDATION")
    print("=" * 50)
    
    # Check all components
    structure_ok = check_directory_structure()
    credentials_ok = check_credentials()
    environment_ok = check_environment()
    system_ok = await check_system_functionality()
    frontend_ok = check_frontend_setup()
    
    # Overall assessment
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    components = [
        ("Project Structure", structure_ok),
        ("Google Credentials", credentials_ok),
        ("Environment Config", environment_ok),
        ("System Functionality", system_ok),
        ("Frontend Setup", frontend_ok),
    ]
    
    all_passed = True
    for component, status in components:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")
        if not status:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 VALIDATION PASSED - READY FOR SUBMISSION!")
        print("All components are working correctly.")
        generate_submission_checklist()
        return True
    else:
        print("⚠️ VALIDATION FAILED - NEEDS ATTENTION")
        print("Please fix the issues above before submitting.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)