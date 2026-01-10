#!/usr/bin/env python3
"""
Debug DB → Sheet sync specifically
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

async def debug_db_to_sheet():
    print("🔍 Debugging DB → Sheet sync...")
    
    try:
        await init_db()
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No sync config found!")
                return
            
            print(f"✅ Config: {config.table_name} → {config.sheet_name}")
            print(f"   Column mapping: {config.column_mapping}")
            
            # Step 1: Get database data
            mysql_service = MySQLService()
            db_data = await mysql_service.get_all_data(config.table_name)
            print(f"\n📊 Database data ({len(db_data)} records):")
            for i, row in enumerate(db_data):
                print(f"   {i+1}: {dict(row)}")
            
            if not db_data:
                print("❌ No data in database!")
                return
            
            # Step 2: Prepare sheet data
            headers = list(db_data[0].keys())
            print(f"\n📋 Database headers: {headers}")
            
            # Create reverse mapping
            reverse_mapping = {v: k for k, v in config.column_mapping.items()}
            print(f"🔄 Reverse mapping: {reverse_mapping}")
            
            # Map to sheet headers
            sheet_headers = [reverse_mapping.get(h, h) for h in headers]
            print(f"📝 Sheet headers: {sheet_headers}")
            
            # Convert data
            sheet_rows = [sheet_headers]
            for row in db_data:
                sheet_row = [str(row.get(h, '')) for h in headers]
                sheet_rows.append(sheet_row)
                print(f"   Row: {sheet_row}")
            
            # Step 3: Update Google Sheet
            sheets_service = SheetsService()
            print(f"\n🚀 Updating Google Sheet...")
            await sheets_service.update_data(config.sheet_id, f"{config.sheet_name}!A:Z", sheet_rows)
            print(f"✅ Updated Google Sheet with {len(db_data)} rows!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_db_to_sheet())