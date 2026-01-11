#!/usr/bin/env python3
"""
Database → Sheet sync ONLY (for testing database changes)
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from sqlalchemy import select
from app.models import SyncConfig

async def db_to_sheet_only():
    """Run only Database → Sheet sync"""
    print("🔄 DATABASE → SHEET SYNC ONLY")
    print("=" * 40)
    
    try:
        await init_db()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No employees config found!")
                return False
        
        print("🔄 Running Database → Sheet sync...")
        await sync_service._sync_db_to_sheet(config)
        print("✅ Database → Sheet sync completed!")
        
        print("\n🎯 Check your Google Sheet now!")
        print("It should show your database changes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(db_to_sheet_only())
    if not success:
        sys.exit(1)