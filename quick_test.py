#!/usr/bin/env python3
"""
Quick test script for manual sync testing
Replaces the individual debug scripts with a unified approach
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from sqlalchemy import select
from app.models import SyncConfig

async def quick_test():
    """Quick test of the sync system"""
    print("🔄 Quick Sync Test")
    print("=" * 30)
    
    try:
        # Initialize
        await init_db()
        print("✅ Database initialized")
        
        # Get sync config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No sync configuration found!")
                print("   Run: python setup_demo.py")
                return False
            
            print(f"✅ Using config: {config.sheet_name} ↔ {config.table_name}")
            
            # Test bidirectional sync
            print("\n🔄 Testing Sheet → DB sync...")
            await sync_service._sync_sheet_to_db(config)
            print("✅ Sheet → DB completed")
            
            print("\n🔄 Testing DB → Sheet sync...")
            await sync_service._sync_db_to_sheet(config)
            print("✅ DB → Sheet completed")
            
            print("\n🎉 Quick test completed successfully!")
            print("\n📋 Next steps:")
            print("1. Check your Google Sheet for updates")
            print("2. Open DB Browser for SQLite to view database")
            print("3. Run comprehensive tests: python test_complete_system.py")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if not success:
        sys.exit(1)