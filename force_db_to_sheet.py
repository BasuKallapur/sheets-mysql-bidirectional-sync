#!/usr/bin/env python3
"""
Force sync from Database to Google Sheet only
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from sqlalchemy import select
from app.models import SyncConfig

async def force_db_to_sheet():
    """Force sync from database to sheet"""
    print("🔄 Forcing Database → Sheet Sync")
    print("=" * 40)
    
    try:
        await init_db()
        
        async with AsyncSessionLocal() as db:
            # Get the main sync config
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No employees sync config found!")
                return False
            
            print(f"✅ Found config: {config.sheet_name} ↔ {config.table_name}")
            
            # Check what's in database
            from app.mysql import MySQLService
            mysql = MySQLService()
            db_data = await mysql.get_all_data('employees')
            print(f"📊 Database has {len(db_data)} rows")
            
            if len(db_data) == 0:
                print("⚠️  Database is empty - will clear the sheet")
            else:
                print("📋 Sample database data:")
                for i, row in enumerate(db_data[:3]):
                    print(f"  Row {i+1}: {dict(row)}")
            
            # Force DB → Sheet sync only
            print("\n🔄 Syncing Database → Sheet...")
            await sync_service._sync_db_to_sheet(config)
            print("✅ Database → Sheet sync completed!")
            
            print("\n🎯 Check your Google Sheet now - it should match the database!")
            return True
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(force_db_to_sheet())
    if not success:
        sys.exit(1)