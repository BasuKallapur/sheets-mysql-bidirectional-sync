#!/usr/bin/env python3
"""
Debug Sheet → DB sync specifically
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, init_db
from sqlalchemy import select
from app.models import SyncConfig
from app.mysql import MySQLService
from app.sheets import SheetsService

async def debug_sheet_to_db():
    print("🔍 Debugging Sheet → DB sync...")
    
    try:
        await init_db()
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No sync config found!")
                return
            
            print(f"✅ Config: {config.sheet_name} → {config.table_name}")
            print(f"   Column mapping: {config.column_mapping}")
            
            # Step 1: Get Google Sheet data
            sheets_service = SheetsService()
            sheet_data = await sheets_service.get_data(config.sheet_id, f"{config.sheet_name}!A:Z")
            
            print(f"\n📊 Google Sheet data ({len(sheet_data)} rows):")
            for i, row in enumerate(sheet_data):
                print(f"   Row {i+1}: {row}")
            
            if len(sheet_data) <= 1:
                print("❌ No data rows in sheet (only headers)!")
                return
            
            # Step 2: Convert to database format
            headers = sheet_data[0]
            rows = sheet_data[1:]
            
            print(f"\n📋 Sheet headers: {headers}")
            
            data_dicts = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        db_column = config.column_mapping.get(header, header)
                        row_dict[db_column] = row[i]
                    else:
                        db_column = config.column_mapping.get(header, header)
                        row_dict[db_column] = ""
                
                # Only add rows that have at least a name
                if row_dict.get('name', '').strip():
                    data_dicts.append(row_dict)
                    print(f"   Converted: {row_dict}")
            
            # Step 3: Update database
            mysql_service = MySQLService()
            print(f"\n🚀 Updating database...")
            await mysql_service.clear_and_insert(config.table_name, data_dicts)
            print(f"✅ Updated database with {len(data_dicts)} rows!")
            
            # Step 4: Verify database content
            print(f"\n🔍 Database now contains:")
            db_data = await mysql_service.get_all_data(config.table_name)
            for i, row in enumerate(db_data):
                print(f"   {i+1}: {dict(row)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_sheet_to_db())