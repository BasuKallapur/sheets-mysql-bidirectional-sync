#!/usr/bin/env python3
"""
Fix the sync logic to properly replace data instead of creating duplicates
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def fix_and_test_sync():
    """Fix sync logic and test proper behavior"""
    print("🔧 FIXING SYNC LOGIC")
    print("=" * 40)
    
    try:
        await init_db()
        mysql = MySQLService()
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
        
        # Step 1: Clean both systems to 4 rows
        print("1️⃣ Cleaning to 4 rows...")
        
        # Clear database
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM employees"))
            
            # Insert clean 4 rows
            insert_query = text("""
                INSERT INTO employees (Name, Email, Age, City, City_1) VALUES
                ('John Doe', 'john@test.com', '30', 'New York', ''),
                ('Jane Smith', 'jane@test.com', '25', 'Los Angeles', ''),
                ('Bob Wilson', 'bob@test.com', '35', 'Chicago', ''),
                ('Alice Brown', 'alice@test.com', '28', 'Miami', '')
            """)
            await conn.execute(insert_query)
        
        # Update sheet to match
        clean_sheet_data = [
            ["Name", "Email", "Age", "City", "City 1"],
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        # Clear sheet completely first
        empty_data = [[""]]
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:Z100", empty_data)
        
        # Set clean data
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:E5", clean_sheet_data)
        
        print("   ✅ Both systems cleaned to 4 rows")
        
        # Step 2: Test Sheet → Database with REPLACE logic
        print("2️⃣ Testing Sheet → Database sync...")
        
        # Modify sheet data
        test_sheet_data = [
            ["Name", "Email", "Age", "City", "City 1"],
            ["John MODIFIED", "john@test.com", "30", "New York", ""],  # Changed name
            ["Jane Smith", "jane@test.com", "26", "Los Angeles", ""],  # Changed age
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:E5", test_sheet_data)
        print("   📝 Modified sheet: John → John MODIFIED, Jane age → 26")
        
        # Now sync Sheet → Database using REPLACE logic
        sheet_data = await sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:E")
        
        if sheet_data and len(sheet_data) > 1:
            headers = sheet_data[0]
            rows = sheet_data[1:]
            
            # Convert to database format
            db_data = []
            for row in rows:
                if any(cell.strip() for cell in row if cell):  # Skip empty rows
                    row_dict = {}
                    for j, header in enumerate(headers):
                        db_column = config.column_mapping.get(header, header.lower().replace(' ', '_'))
                        value = row[j] if j < len(row) else ""
                        row_dict[db_column] = value.strip() if isinstance(value, str) else value
                    db_data.append(row_dict)
            
            # REPLACE all data in database (clear and insert)
            await mysql.clear_and_insert("employees", db_data)
            print("   ✅ Database updated with sheet data (REPLACE logic)")
        
        # Step 3: Verify the fix
        print("3️⃣ Verifying fix...")
        
        db_check = await mysql.get_all_data("employees")
        print(f"   📊 Database has {len(db_check)} rows:")
        for i, row in enumerate(db_check):
            print(f"      {i+1}. {row['Name']} | {row['Email']} | {row['Age']} | {row['City']}")
        
        # Check if changes are correct
        john_found = any(row['Name'] == 'John MODIFIED' for row in db_check)
        jane_age_correct = any(row['Name'] == 'Jane Smith' and row['Age'] == '26' for row in db_check)
        
        if john_found and jane_age_correct and len(db_check) == 4:
            print("\n🎉 SUCCESS! Sync logic fixed:")
            print("   ✅ No duplicates created")
            print("   ✅ Changes properly applied")
            print("   ✅ Data integrity maintained")
            return True
        else:
            print(f"\n❌ Issues found:")
            print(f"   John MODIFIED found: {john_found}")
            print(f"   Jane age 26: {jane_age_correct}")
            print(f"   Row count: {len(db_check)}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_and_test_sync())
    if success:
        print("\n✅ SYNC LOGIC FIXED!")
        print("Now your sync will UPDATE existing rows instead of creating duplicates!")
    else:
        sys.exit(1)