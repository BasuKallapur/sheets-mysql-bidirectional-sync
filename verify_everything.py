#!/usr/bin/env python3
"""
Complete verification script for Superjoin assignment
Tests all components to ensure everything works perfectly
"""
import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_file_structure():
    """Verify all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        "README.md",
        "requirements.txt", 
        "setup_demo.py",
        "test_complete_system.py",
        "quick_test.py",
        "validate_submission.py",
        "app/main.py",
        "app/sync.py",
        "app/mysql.py",
        "app/sheets.py",
        "app/models.py",
        "app/config.py",
        "app/database.py",
        "frontend/package.json",
        "frontend/pages/index.tsx",
        "frontend/components/SyncConfigForm.tsx",
        "frontend/components/SyncConfigList.tsx",
        "frontend/components/SyncMonitor.tsx",
        "credentials.json",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    # Check Python dependencies
    python_deps = run_command("pip list", "Python dependencies check")
    
    # Check if frontend dependencies exist
    frontend_deps = Path("frontend/node_modules").exists()
    if frontend_deps:
        print("✅ Frontend dependencies - SUCCESS")
    else:
        print("❌ Frontend dependencies - MISSING")
        print("   Run: cd frontend && npm install")
    
    return python_deps and frontend_deps

async def run_system_tests():
    """Run all system tests"""
    print("\n🧪 Running system tests...")
    
    # Add current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run comprehensive tests
        from test_complete_system import SystemTester
        
        tester = SystemTester()
        success = await tester.run_all_tests()
        
        return success
        
    except Exception as e:
        print(f"❌ System tests failed: {e}")
        return False

def check_google_credentials():
    """Verify Google credentials are valid"""
    print("\n🔑 Checking Google credentials...")
    
    if not Path("credentials.json").exists():
        print("❌ credentials.json not found")
        return False
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            
        required_fields = ["client_email", "private_key", "project_id"]
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Missing credential fields: {missing_fields}")
            return False
        else:
            print(f"✅ Valid credentials for: {creds['client_email']}")
            return True
            
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def generate_final_report(results):
    """Generate final verification report"""
    print("\n" + "="*60)
    print("📊 FINAL VERIFICATION REPORT")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Success Rate: {(passed_checks/total_checks)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    if passed_checks == total_checks:
        print("\n🎉 VERIFICATION PASSED - READY FOR DEMO!")
        print("\n🚀 Next Steps:")
        print("1. Start backend: python -m uvicorn app.main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open dashboard: http://localhost:3000")
        print("4. Record demo video")
        print("5. Submit to Superjoin!")
        return True
    else:
        print("\n⚠️ VERIFICATION FAILED - NEEDS ATTENTION")
        print("Please fix the failed checks above before proceeding.")
        return False

async def main():
    """Main verification function"""
    print("🔍 SUPERJOIN ASSIGNMENT - COMPLETE VERIFICATION")
    print("="*60)
    
    results = {}
    
    # Run all verification checks
    results["File Structure"] = check_file_structure()
    results["Dependencies"] = check_dependencies()
    results["Google Credentials"] = check_google_credentials()
    results["System Tests"] = await run_system_tests()
    
    # Generate final report
    success = generate_final_report(results)
    
    # Save results
    with open("verification_results.json", "w") as f:
        json.dump({
            "timestamp": str(asyncio.get_event_loop().time()),
            "results": results,
            "overall_success": success
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: verification_results.json")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)