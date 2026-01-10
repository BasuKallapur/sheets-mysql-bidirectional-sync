#!/usr/bin/env python3
"""
Quick test script to manually trigger sync
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.sync import sync_service
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import SyncConfig

async def test_sync():
    print("🔄 Testing sync manually...")
    
    try:
        # Initialize database first
        from app.database import init_db
        await init_db()
        print("✅ Database initialized")
        
        async with AsyncSessionLocal() as db:
            # Get the first sync config
            result = await db.execute(select(SyncConfig))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No sync configuration found!")
                return
            
            print(f"✅ Found sync config: {config.sheet_id}")
            print(f"   Sheet: {config.sheet_name}")
            print(f"   Table: {config.table_name}")
            print(f"   Column mapping: {config.column_mapping}")
            
            # Test both directions
            print("\n🔄 Testing Sheet → DB sync...")
            await sync_service._sync_sheet_to_db(config)
            print("✅ Sheet → DB sync completed!")
            
            print("\n🔄 Testing DB → Sheet sync...")
            
            # Debug: Check what data is in the database
            from app.mysql import MySQLService
            mysql_service = MySQLService()
            db_data = await mysql_service.get_all_data(config.table_name)
            print(f"📊 Database has {len(db_data)} records:")
            for i, row in enumerate(db_data[:3]):  # Show first 3 records
                print(f"   Row {i+1}: {row}")
            
            await sync_service._sync_db_to_sheet(config)
            print("✅ DB → Sheet sync completed!")
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sync())