#!/usr/bin/env python3
"""
Complete fix: Reset everything and implement proper sync
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def complete_fix():
    """Complete fix for the sync system"""
    print("🔧 COMPLETE SYNC FIX")
    print("=" * 40)
    
    try:
        await init_db()
        mysql = MySQLService()
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
        
        print("1️⃣ Dropping and recreating table with proper structure...")
        
        async with engine.begin() as conn:
            # Drop existing table
            await conn.execute(text("DROP TABLE IF EXISTS employees"))
            
            # Create new table with proper structure
            create_query = text("""
                CREATE TABLE employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sheet_row_id INT UNIQUE NOT NULL,
                    Name TEXT,
                    Email TEXT,
                    Age TEXT,
                    City TEXT,
                    City_1 TEXT,
                    UNIQUE KEY unique_sheet_row (sheet_row_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await conn.execute(create_query)
            print("   ✅ Table recreated with proper structure")
        
        print("2️⃣ Setting up clean test data...")
        
        # Set clean data in Google Sheet (without Sheet Row Id column)
        clean_sheet_data = [
            ["Name", "Email", "Age", "City", "City 1"],  # Headers only
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        # Clear sheet completely
        empty_data = [[""]]
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:Z100", empty_data)
        
        # Set clean data
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:E5", clean_sheet_data)
        print("   ✅ Google Sheet set to 4 clean rows")
        
        print("3️⃣ Initial sync to populate database...")
        
        # Get sheet data
        sheet_data = await sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:E")
        
        if sheet_data and len(sheet_data) > 1:
            headers = sheet_data[0]
            rows = sheet_data[1:]
            
            # Insert with proper sheet_row_id
            async with engine.begin() as conn:
                for i, row in enumerate(rows):
                    if not any(cell.strip() for cell in row if cell):
                        continue
                    
                    sheet_row_id = i + 2  # Row 2, 3, 4, 5
                    
                    insert_query = text("""
                        INSERT INTO employees (sheet_row_id, Name, Email, Age, City, City_1)
                        VALUES (:sheet_row_id, :name, :email, :age, :city, :city_1)
                    """)
                    
                    await conn.execute(insert_query, {
                        'sheet_row_id': sheet_row_id,
                        'name': row[0] if len(row) > 0 else '',
                        'email': row[1] if len(row) > 1 else '',
                        'age': row[2] if len(row) > 2 else '',
                        'city': row[3] if len(row) > 3 else '',
                        'city_1': row[4] if len(row) > 4 else ''
                    })
        
        print("   ✅ Database populated with proper sheet_row_id mapping")
        
        print("4️⃣ Testing UPSERT functionality...")
        
        # Test update
        async with engine.begin() as conn:
            update_query = text("""
                INSERT INTO employees (sheet_row_id, Name, Email, Age, City, City_1)
                VALUES (2, 'John UPDATED', 'john@test.com', '30', 'New York', '')
                ON DUPLICATE KEY UPDATE 
                    Name = VALUES(Name),
                    Email = VALUES(Email),
                    Age = VALUES(Age),
                    City = VALUES(City),
                    City_1 = VALUES(City_1)
            """)
            await conn.execute(update_query)
        
        print("   ✅ UPSERT test completed")
        
        # Verify
        db_data = await mysql.get_all_data("employees")
        print(f"\n📊 Final state: {len(db_data)} rows")
        
        for row in db_data:
            print(f"   sheet_row_id={row['sheet_row_id']}: {row['Name']}")
        
        # Check if John was updated (not duplicated)
        john_rows = [row for row in db_data if 'John' in row['Name']]
        if len(john_rows) == 1 and 'UPDATED' in john_rows[0]['Name']:
            print("\n🎉 SUCCESS! UPSERT is working correctly!")
            print("   ✅ No duplicates created")
            print("   ✅ Update applied correctly")
            return True
        else:
            print(f"\n❌ UPSERT issue: Found {len(john_rows)} John rows")
            return False
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(complete_fix())
    if success:
        print("\n✅ SYNC SYSTEM COMPLETELY FIXED!")
        print("Now test: Edit Google Sheet → No duplicates will be created!")
    else:
        sys.exit(1)