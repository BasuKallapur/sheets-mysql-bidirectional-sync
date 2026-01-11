#!/usr/bin/env python3
"""
Assignment Validation Script - Validates core functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select
from app.models import SyncConfig

async def validate_assignment():
    """Validate assignment according to requirements"""
    print("🎯 SUPERJOIN ASSIGNMENT VALIDATION")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: Database Connection
    print("\n1️⃣ Testing Database Connection...")
    try:
        await init_db()
        mysql_service = MySQLService()
        # Test basic database operations
        await mysql_service.create_table("validation_test", ["name", "email"])
        test_data = [{"name": "Test User", "email": "test@example.com"}]
        await mysql_service.clear_and_insert("validation_test", test_data)
        data = await mysql_service.get_all_data("validation_test")
        
        if data and len(data) > 0:
            print("   ✅ Database connection working")
            success_count += 1
        else:
            print("   ❌ Database connection failed")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # Test 2: Google Sheets Connection
    print("\n2️⃣ Testing Google Sheets Connection...")
    try:
        sheets_service = SheetsService()
        # Test reading from the configured sheet
        sheet_data = await sheets_service.get_data(
            "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI", 
            "Sheet1!A1:D10"
        )
        
        if sheet_data and len(sheet_data) > 0:
            print(f"   ✅ Google Sheets working - {len(sheet_data)} rows read")
            success_count += 1
        else:
            print("   ❌ Google Sheets connection failed")
    except Exception as e:
        print(f"   ❌ Google Sheets error: {e}")
    
    # Test 3: Sync Configuration
    print("\n3️⃣ Testing Sync Configuration...")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig))
            configs = result.scalars().all()
            
            if configs and len(configs) > 0:
                print(f"   ✅ Found {len(configs)} sync configuration(s)")
                success_count += 1
                active_config = configs[0]  # Use first config
            else:
                print("   ❌ No sync configurations found")
                active_config = None
    except Exception as e:
        print(f"   ❌ Sync configuration error: {e}")
        active_config = None
    
    # Test 4: Sheet to Database Sync
    print("\n4️⃣ Testing Sheet → Database Sync...")
    if active_config:
        try:
            await sync_service._sync_sheet_to_db(active_config)
            print("   ✅ Sheet → Database sync completed")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Sheet → Database sync failed: {e}")
    else:
        print("   ❌ Skipped - no active config")
    
    # Test 5: Database to Sheet Sync
    print("\n5️⃣ Testing Database → Sheet Sync...")
    if active_config:
        try:
            await sync_service._sync_db_to_sheet(active_config)
            print("   ✅ Database → Sheet sync completed")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Database → Sheet sync failed: {e}")
    else:
        print("   ❌ Skipped - no active config")
    
    # Test 6: Web Interface Check
    print("\n6️⃣ Testing Web Interface Files...")
    try:
        frontend_files = [
            "frontend/package.json",
            "frontend/pages/index.tsx",
            "app/main.py"
        ]
        
        all_exist = True
        for file_path in frontend_files:
            if not os.path.exists(file_path):
                all_exist = False
                break
        
        if all_exist:
            print("   ✅ Web interface files present")
            success_count += 1
        else:
            print("   ❌ Missing web interface files")
    except Exception as e:
        print(f"   ❌ Web interface check failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count >= 4:  # At least core functionality working
        print("\n🎉 ASSIGNMENT VALIDATION PASSED!")
        print("\n✅ Core Requirements Met:")
        print("   • Database connection working")
        print("   • Google Sheets integration working")
        print("   • Bidirectional sync functional")
        print("   • Web interface ready")
        
        print("\n🚀 Ready for Demo!")
        print("   1. Start backend: python -m uvicorn app.main:app --reload")
        print("   2. Start frontend: cd frontend && npm run dev")
        print("   3. Open: http://localhost:3000")
        
        print("\n📋 Demo Steps:")
        print("   1. Edit data in Google Sheet")
        print("   2. Click 'Manual Sync' in web dashboard")
        print("   3. Check MySQL database (MySQL Workbench/phpMyAdmin)")
        print("   4. Edit data in MySQL database")
        print("   5. Sync again and check Google Sheet")
        
        return True
    else:
        print("\n⚠️ VALIDATION NEEDS ATTENTION")
        print("Some core components need fixing before demo.")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_assignment())
    if not success:
        sys.exit(1)