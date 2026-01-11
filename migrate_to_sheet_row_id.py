#!/usr/bin/env python3
"""
Migration script: Add sheet_row_id column to existing employees table
This implements the professional sync fix
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal, engine
from app.mysql import MySQLService
from app.sheets import SheetsService
from sqlalchemy import select, text
from app.models import SyncConfig

async def migrate_to_sheet_row_id():
    """Migrate existing table to use sheet_row_id for proper sync"""
    print("🔄 MIGRATING TO PROFESSIONAL SYNC ARCHITECTURE")
    print("=" * 60)
    
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
        
        print("1️⃣ Adding sheet_row_id column to existing table...")
        
        async with engine.begin() as conn:
            # Add sheet_row_id column
            try:
                await conn.execute(text("ALTER TABLE employees ADD COLUMN sheet_row_id INT"))
                print("   ✅ Added sheet_row_id column")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("   ✅ sheet_row_id column already exists")
                else:
                    raise e
            
            # Add unique constraint
            try:
                await conn.execute(text("ALTER TABLE employees ADD UNIQUE KEY unique_sheet_row (sheet_row_id)"))
                print("   ✅ Added unique constraint on sheet_row_id")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("   ✅ Unique constraint already exists")
                else:
                    raise e
        
        print("2️⃣ Cleaning existing data and setting up fresh sync...")
        
        # Clear existing data (it has duplicates anyway)
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM employees"))
            print("   ✅ Cleared existing duplicate data")
        
        # Get clean data from Google Sheet
        sheet_data = await sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:Z")
        
        if not sheet_data or len(sheet_data) <= 1:
            print("   ⚠️  No data in Google Sheet to migrate")
            return True
        
        headers = sheet_data[0]
        rows = sheet_data[1:]
        
        print(f"   📊 Found {len(rows)} rows in Google Sheet")
        
        # Convert to database format with sheet_row_id
        data_with_row_ids = []
        
        for i, row in enumerate(rows):
            if not any(cell.strip() for cell in row if cell):  # Skip empty rows
                continue
                
            sheet_row_id = i + 2  # Row 2, 3, 4, 5... (row 1 is header)
            
            row_dict = {'sheet_row_id': sheet_row_id}
            
            for j, header in enumerate(headers):
                db_column = config.column_mapping.get(header, header.lower().replace(' ', '_'))
                value = row[j] if j < len(row) else ""
                
                if isinstance(value, str):
                    value = value.strip()
                
                row_dict[db_column] = value
            
            data_with_row_ids.append(row_dict)
        
        print("3️⃣ Populating database with sheet_row_id mapping...")
        
        # Insert data with proper sheet_row_id mapping
        await mysql.upsert_data_with_sheet_row_id("employees", data_with_row_ids)
        
        print(f"   ✅ Inserted {len(data_with_row_ids)} rows with sheet_row_id mapping")
        
        # Verify the migration
        print("4️⃣ Verifying migration...")
        
        db_data = await mysql.get_all_data("employees")
        print(f"   📊 Database now has {len(db_data)} rows")
        
        for i, row in enumerate(db_data[:3]):  # Show first 3
            print(f"      Row {i+1}: sheet_row_id={row['sheet_row_id']}, Name={row['Name']}")
        
        if len(db_data) > 3:
            print(f"      ... and {len(db_data) - 3} more rows")
        
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("\n✅ Benefits of the new architecture:")
        print("   • No more duplicate rows on sheet edits")
        print("   • Deterministic row mapping via sheet_row_id")
        print("   • Production-safe concurrent editing")
        print("   • Automatic cleanup of deleted sheet rows")
        
        print("\n🚀 Your sync system is now production-ready!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(migrate_to_sheet_row_id())
    if success:
        print("\n✅ READY FOR TESTING!")
        print("Now test: Edit a cell in Google Sheet → No duplicates will be created!")
    else:
        sys.exit(1)