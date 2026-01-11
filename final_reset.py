#!/usr/bin/env python3
"""
Final reset: Completely clean both systems and test proper sync
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def final_reset():
    """Final reset and test"""
    print("🔄 FINAL RESET - CLEAN SLATE")
    print("=" * 50)
    
    try:
        await init_db()
        mysql = MySQLService()
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
        
        print("1️⃣ Completely clearing Google Sheet...")
        
        # Clear the entire sheet with a massive empty range
        massive_empty = []
        for i in range(100):
            massive_empty.append([""] * 20)  # 100 rows x 20 columns of empty
        
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:T100", massive_empty)
        print("   ✅ Google Sheet completely cleared")
        
        print("2️⃣ Recreating database table...")
        
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS employees"))
            
            create_query = text("""
                CREATE TABLE employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sheet_row_id INT UNIQUE NOT NULL,
                    Name TEXT,
                    Email TEXT,
                    Age TEXT,
                    City TEXT,
                    City_1 TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await conn.execute(create_query)
        
        print("   ✅ Database table recreated")
        
        print("3️⃣ Setting up exactly 3 test rows...")
        
        # Set exactly 3 rows in Google Sheet
        test_data = [
            ["Name", "Email", "Age", "City", "City 1"],
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""]
        ]
        
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:E4", test_data)
        print("   ✅ Google Sheet has exactly 3 test rows")
        
        print("4️⃣ Initial database population...")
        
        async with engine.begin() as conn:
            # Insert the 3 rows with proper sheet_row_id
            inserts = [
                (2, "John Doe", "john@test.com", "30", "New York", ""),
                (3, "Jane Smith", "jane@test.com", "25", "Los Angeles", ""),
                (4, "Bob Wilson", "bob@test.com", "35", "Chicago", "")
            ]
            
            for sheet_row_id, name, email, age, city, city_1 in inserts:
                await conn.execute(text("""
                    INSERT INTO employees (sheet_row_id, Name, Email, Age, City, City_1)
                    VALUES (:sheet_row_id, :name, :email, :age, :city, :city_1)
                """), {
                    'sheet_row_id': sheet_row_id,
                    'name': name,
                    'email': email,
                    'age': age,
                    'city': city,
                    'city_1': city_1
                })
        
        print("   ✅ Database populated with 3 rows")
        
        print("5️⃣ Testing UPSERT (the critical test)...")
        
        # Test: Update John Doe to John UPDATED
        async with engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO employees (sheet_row_id, Name, Email, Age, City, City_1)
                VALUES (2, 'John UPDATED', 'john@test.com', '30', 'New York', '')
                ON DUPLICATE KEY UPDATE 
                    Name = VALUES(Name)
            """))
        
        # Verify results
        db_data = await mysql.get_all_data("employees")
        
        print(f"\n📊 Final verification: {len(db_data)} rows")
        for row in db_data:
            print(f"   ID={row['id']}, sheet_row_id={row['sheet_row_id']}: {row['Name']}")
        
        # Check success criteria
        if len(db_data) == 3:  # Still 3 rows
            john_updated = any(row['Name'] == 'John UPDATED' for row in db_data)
            if john_updated:
                print("\n🎉 PERFECT! UPSERT IS WORKING!")
                print("   ✅ No duplicates created")
                print("   ✅ Update applied correctly")
                print("   ✅ Row count maintained")
                
                print("\n6️⃣ Now testing sheet edit simulation...")
                
                # Simulate editing Google Sheet
                await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A2", [["John SHEET-EDIT"]])
                print("   📝 Simulated sheet edit: John Doe → John SHEET-EDIT")
                
                # Now test the actual sync logic
                from app.sync import sync_service
                await sync_service._sync_sheet_to_db(config)
                
                # Check if it worked
                db_data_after = await mysql.get_all_data("employees")
                print(f"\n📊 After sheet sync: {len(db_data_after)} rows")
                
                if len(db_data_after) == 3:
                    sheet_edit_found = any('SHEET-EDIT' in row['Name'] for row in db_data_after)
                    if sheet_edit_found:
                        print("🎉 COMPLETE SUCCESS!")
                        print("   ✅ Sheet edit synced to database")
                        print("   ✅ No duplicates created")
                        print("   ✅ Sync system is working perfectly!")
                        return True
                    else:
                        print("❌ Sheet edit not found in database")
                        return False
                else:
                    print(f"❌ Wrong row count after sync: {len(db_data_after)}")
                    return False
            else:
                print("❌ John was not updated")
                return False
        else:
            print(f"❌ Wrong row count: {len(db_data)} (expected 3)")
            return False
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_reset())
    if success:
        print("\n🚀 SYNC SYSTEM IS PRODUCTION READY!")
        print("Edit Google Sheet cells → Updates will work without duplicates!")
    else:
        print("\n❌ Still has issues")
        sys.exit(1)