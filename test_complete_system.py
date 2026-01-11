#!/usr/bin/env python3
"""
Comprehensive test script for Superjoin Sync System
Tests all aspects of bidirectional sync functionality
"""
import asyncio
import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select
from app.models import SyncConfig

class SystemTester:
    def __init__(self):
        self.mysql_service = MySQLService()
        self.sheets_service = SheetsService()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_database_connection(self):
        """Test database connectivity and table creation"""
        try:
            await init_db()
            
            # Test table creation
            await self.mysql_service.create_table("test_table", ["name", "email"])
            
            # Test data insertion
            test_data = [{"name": "Test User", "email": "test@example.com"}]
            await self.mysql_service.clear_and_insert("test_table", test_data)
            
            # Test data retrieval
            data = await self.mysql_service.get_all_data("test_table")
            
            self.log_test("Database Connection", len(data) == 1, f"Retrieved {len(data)} records")
            return True
            
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    async def test_google_sheets_connection(self):
        """Test Google Sheets API connectivity"""
        try:
            # Test reading from sheet
            sheet_data = await self.sheets_service.get_data(
                "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI", 
                "Sheet1!A1:D1"
            )
            
            if sheet_data and len(sheet_data) > 0:
                self.log_test("Google Sheets Read", True, f"Read {len(sheet_data)} rows")
                
                # Test writing to sheet (append a timestamp)
                test_data = [["Test", "test@example.com", "25", "Test City"]]
                await self.sheets_service.update_data(
                    "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI",
                    "Sheet1!A2:D2",
                    test_data
                )
                self.log_test("Google Sheets Write", True, "Successfully wrote test data")
                return True
            else:
                self.log_test("Google Sheets Read", False, "No data retrieved")
                return False
                
        except Exception as e:
            self.log_test("Google Sheets Connection", False, str(e))
            return False
    
    async def test_sync_configuration(self):
        """Test sync configuration creation and management"""
        try:
            async with AsyncSessionLocal() as db:
                # Create test sync config
                config = await sync_service.create_sync(
                    db=db,
                    sheet_id="1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI",
                    sheet_name="Sheet1",
                    table_name="test_employees",
                    column_mapping={
                        "Name": "name",
                        "Email": "email",
                        "Age": "age", 
                        "City": "city"
                    }
                )
                
                # Verify config was saved
                result = await db.execute(select(SyncConfig).where(SyncConfig.id == config.id))
                saved_config = result.scalar_one_or_none()
                
                if saved_config:
                    self.log_test("Sync Configuration", True, f"Config ID: {config.id}")
                    return config
                else:
                    self.log_test("Sync Configuration", False, "Config not saved properly")
                    return None
                    
        except Exception as e:
            self.log_test("Sync Configuration", False, str(e))
            return None
    
    async def test_sheet_to_db_sync(self, config):
        """Test Google Sheet → Database sync"""
        try:
            # Perform sync
            await sync_service._sync_sheet_to_db(config)
            
            # Verify data was synced
            db_data = await self.mysql_service.get_all_data(config.table_name)
            
            if db_data and len(db_data) > 0:
                self.log_test("Sheet → DB Sync", True, f"Synced {len(db_data)} records")
                return True
            else:
                self.log_test("Sheet → DB Sync", False, "No data synced to database")
                return False
                
        except Exception as e:
            self.log_test("Sheet → DB Sync", False, str(e))
            return False
    
    async def test_db_to_sheet_sync(self, config):
        """Test Database → Google Sheet sync"""
        try:
            # Add test data to database
            test_data = [
                {"name": "DB Test User", "email": "dbtest@example.com", "age": "30", "city": "DB City"}
            ]
            await self.mysql_service.clear_and_insert(config.table_name, test_data)
            
            # Perform sync
            await sync_service._sync_db_to_sheet(config)
            
            # Verify by reading sheet data
            sheet_data = await self.sheets_service.get_data(
                config.sheet_id, 
                f"{config.sheet_name}!A:D"
            )
            
            if sheet_data and len(sheet_data) > 1:  # Headers + data
                self.log_test("DB → Sheet Sync", True, f"Sheet has {len(sheet_data)} rows")
                return True
            else:
                self.log_test("DB → Sheet Sync", False, "No data found in sheet after sync")
                return False
                
        except Exception as e:
            self.log_test("DB → Sheet Sync", False, str(e))
            return False
    
    async def test_bidirectional_sync(self, config):
        """Test full bidirectional sync"""
        try:
            # Test 1: Sheet → DB → Sheet
            print("    Testing Sheet → DB → Sheet cycle...")
            
            # Get initial sheet data
            initial_sheet = await self.sheets_service.get_data(
                config.sheet_id, f"{config.sheet_name}!A:D"
            )
            
            # Sync to DB
            await sync_service._sync_sheet_to_db(config)
            
            # Sync back to sheet
            await sync_service._sync_db_to_sheet(config)
            
            # Verify sheet data is consistent
            final_sheet = await self.sheets_service.get_data(
                config.sheet_id, f"{config.sheet_name}!A:D"
            )
            
            if len(initial_sheet) == len(final_sheet):
                self.log_test("Bidirectional Sync", True, "Data consistency maintained")
                return True
            else:
                self.log_test("Bidirectional Sync", False, f"Data mismatch: {len(initial_sheet)} vs {len(final_sheet)}")
                return False
                
        except Exception as e:
            self.log_test("Bidirectional Sync", False, str(e))
            return False
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        try:
            # Test invalid sheet ID
            try:
                await self.sheets_service.get_data("invalid_sheet_id", "Sheet1!A1:A1")
                self.log_test("Error Handling - Invalid Sheet", False, "Should have thrown error")
            except:
                self.log_test("Error Handling - Invalid Sheet", True, "Properly handled invalid sheet")
            
            # Test empty data handling
            await self.mysql_service.clear_and_insert("empty_table", [])
            self.log_test("Error Handling - Empty Data", True, "Handled empty data gracefully")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
            return False
    
    async def test_manual_sync_trigger(self):
        """Test manual sync trigger functionality"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(SyncConfig))
                config = result.scalar_one_or_none()
                
                if not config:
                    self.log_test("Manual Sync Trigger", False, "No sync config found")
                    return False
                
                print("    Testing manual sync trigger...")
                
                # Test both directions
                await sync_service._sync_sheet_to_db(config)
                await sync_service._sync_db_to_sheet(config)
                
                self.log_test("Manual Sync Trigger", True, "Manual sync completed successfully")
                return True
                
        except Exception as e:
            self.log_test("Manual Sync Trigger", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Comprehensive System Tests...")
        print("=" * 50)
        
        # Test 1: Database Connection
        db_success = await self.test_database_connection()
        
        # Test 2: Google Sheets Connection
        sheets_success = await self.test_google_sheets_connection()
        
        # Test 3: Sync Configuration
        config = await self.test_sync_configuration()
        
        if config:
            # Test 4: Sheet to DB Sync
            sheet_to_db = await self.test_sheet_to_db_sync(config)
            
            # Test 5: DB to Sheet Sync
            db_to_sheet = await self.test_db_to_sheet_sync(config)
            
            # Test 6: Bidirectional Sync
            bidirectional = await self.test_bidirectional_sync(config)
            
            # Test 7: Manual Sync Trigger
            manual_sync = await self.test_manual_sync_trigger()
        else:
            sheet_to_db = db_to_sheet = bidirectional = manual_sync = False
        
        # Test 8: Error Handling
        error_handling = await self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"]:
                print(f"    {result['message']}")
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Test results saved to: test_results.json")
        
        # Overall success
        all_critical_passed = db_success and sheets_success and config is not None
        if all_critical_passed:
            print("\n🎉 SYSTEM READY FOR DEMO!")
            print("All critical components are working correctly.")
        else:
            print("\n⚠️ SYSTEM NEEDS ATTENTION!")
            print("Some critical components failed. Please check the errors above.")
        
        return all_critical_passed

async def main():
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready to start the demo!")
        print("Run: python -m uvicorn app.main:app --reload")
    else:
        print("\n🔧 Please fix the issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())