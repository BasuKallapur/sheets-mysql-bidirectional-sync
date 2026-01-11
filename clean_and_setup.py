#!/usr/bin/env python3
"""
Clean everything and set up exactly 4 rows for validation
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def clean_and_setup():
    """Clean everything and set up 4 clean rows"""
    print("🧹 CLEANING AND SETTING UP 4 ROWS")
    print("=" * 50)
    
    try:
        await init_db()
        mysql = MySQLService()
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No employees config found!")
                return False
        
        # Step 1: Clear MySQL database completely
        print("1️⃣ Clearing MySQL database...")
        from sqlalchemy import text
        from app.database import engine
        
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE employees"))
        
        # Verify it's empty
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) as count FROM employees"))
            count = result.fetchone()
            print(f"   ✅ MySQL cleared - {count[0]} rows remaining")
        
        # Step 2: Set up exactly 4 rows in MySQL
        print("2️⃣ Adding 4 clean rows to MySQL...")
        
        async with engine.begin() as conn:
            insert_query = text("""
                INSERT INTO employees (Name, Email, Age, City, City_1) VALUES
                ('John Doe', 'john@test.com', '30', 'New York', ''),
                ('Jane Smith', 'jane@test.com', '25', 'Los Angeles', ''),
                ('Bob Wilson', 'bob@test.com', '35', 'Chicago', ''),
                ('Alice Brown', 'alice@test.com', '28', 'Miami', '')
            """)
            await conn.execute(insert_query)
        
        # Verify MySQL has 4 rows
        db_data = await mysql.get_all_data("employees")
        print(f"   ✅ MySQL now has {len(db_data)} rows")
        
        # Step 3: Clear and update Google Sheet
        print("3️⃣ Updating Google Sheet...")
        
        # Prepare sheet data (headers + 4 rows)
        sheet_data = [
            ["Name", "Email", "Age", "City", "City 1"],  # Headers
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        # Clear sheet and add clean data
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A:Z", sheet_data)
        print(f"   ✅ Google Sheet updated with 4 rows")
        
        # Step 4: Verify both are in sync
        print("4️⃣ Verifying sync...")
        
        # Check sheet data
        sheet_check = await sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:E")
        print(f"   📊 Sheet has {len(sheet_check)-1} data rows (excluding header)")
        
        # Check database data
        db_check = await mysql.get_all_data("employees")
        print(f"   📊 Database has {len(db_check)} data rows")
        
        if len(sheet_check) == 5 and len(db_check) == 4:  # 5 = header + 4 rows
            print("\n🎉 SUCCESS! Both systems have exactly 4 rows and are in sync!")
            print("\n📋 Current data:")
            for i, row in enumerate(db_check):
                print(f"   Row {i+1}: {row['Name']} | {row['Email']} | {row['Age']} | {row['City']}")
            
            print("\n✅ Ready for validation testing!")
            return True
        else:
            print(f"\n❌ Sync issue - Sheet: {len(sheet_check)-1} rows, DB: {len(db_check)} rows")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(clean_and_setup())
    if success:
        print("\n🚀 NOW YOU CAN START VALIDATION!")
    else:
        sys.exit(1)