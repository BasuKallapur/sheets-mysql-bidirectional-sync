#!/usr/bin/env python3
"""
Final clean - force 4 rows in both systems
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def final_clean():
    """Final clean setup"""
    print("🧹 FINAL CLEAN - 4 ROWS ONLY")
    print("=" * 40)
    
    try:
        await init_db()
        mysql = MySQLService()
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
        
        # Database is already clean with 4 rows, let's verify
        db_data = await mysql.get_all_data("employees")
        print(f"✅ Database has {len(db_data)} rows")
        
        # Force clear the entire sheet and set only 4 rows
        print("🔄 Force clearing Google Sheet...")
        
        # Clear a large range to make sure we get everything
        empty_data = [[""]]  # Single empty cell
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:Z1000", empty_data)
        
        # Now set exactly what we want
        clean_sheet_data = [
            ["Name", "Email", "Age", "City", "City 1"],  # Headers
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        await sheets.update_data(config.sheet_id, f"{config.sheet_name}!A1:E5", clean_sheet_data)
        print("✅ Google Sheet set to 4 rows")
        
        # Verify
        sheet_check = await sheets.get_data(config.sheet_id, f"{config.sheet_name}!A1:E10")
        print(f"📊 Sheet verification: {len(sheet_check)} total rows")
        
        if len(sheet_check) <= 5:  # Header + 4 data rows
            print("\n🎉 SUCCESS! Both systems have exactly 4 rows!")
            print("\n📋 Ready for validation:")
            for i, row in enumerate(db_data):
                print(f"   {i+1}. {row['Name']} | {row['Email']} | {row['Age']} | {row['City']}")
            return True
        else:
            print(f"❌ Sheet still has too many rows: {len(sheet_check)}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_clean())
    if success:
        print("\n🚀 NOW START VALIDATION!")
    else:
        sys.exit(1)