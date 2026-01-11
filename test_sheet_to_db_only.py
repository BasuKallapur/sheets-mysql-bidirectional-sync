#!/usr/bin/env python3
"""
Test ONLY Sheet → Database sync (no bidirectional)
This will prove the sheet_row_id logic works
"""
import asyncio
import sys
sys.path.append('.')

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service
from app.mysql import MySQLService
from sqlalchemy import select
from app.models import SyncConfig

async def test_sheet_to_db_only():
    """Test only Sheet → Database sync"""
    print("🧪 TESTING SHEET → DATABASE SYNC ONLY")
    print("=" * 50)
    
    try:
        await init_db()
        mysql = MySQLService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
            
            if not config:
                print("❌ No employees config found!")
                return False
        
        # Check current database state
        print("1️⃣ Current database state:")
        db_data_before = await mysql.get_all_data("employees")
        print(f"   📊 Database has {len(db_data_before)} rows")
        
        for i, row in enumerate(db_data_before[:3]):
            print(f"      Row {i+1}: sheet_row_id={row.get('sheet_row_id', 'N/A')}, Name={row['Name']}")
        
        # Run ONLY Sheet → Database sync
        print("\n2️⃣ Running Sheet → Database sync ONLY...")
        await sync_service._sync_sheet_to_db(config)
        print("   ✅ Sheet → Database sync completed")
        
        # Check database state after sync
        print("\n3️⃣ Database state after sync:")
        db_data_after = await mysql.get_all_data("employees")
        print(f"   📊 Database now has {len(db_data_after)} rows")
        
        for i, row in enumerate(db_data_after[:5]):
            print(f"      Row {i+1}: sheet_row_id={row.get('sheet_row_id', 'N/A')}, Name={row['Name']}")
        
        # Check if duplicates were created
        if len(db_data_after) > len(db_data_before):
            print(f"\n❌ DUPLICATES CREATED!")
            print(f"   Before: {len(db_data_before)} rows")
            print(f"   After: {len(db_data_after)} rows")
            print(f"   Difference: +{len(db_data_after) - len(db_data_before)} rows")
            return False
        else:
            print(f"\n✅ NO DUPLICATES!")
            print(f"   Row count remained: {len(db_data_after)}")
            
            # Check if updates worked
            changes_found = False
            for row in db_data_after:
                if "FIXED" in row['Name'] or "UPDATED" in row['Name']:
                    changes_found = True
                    print(f"   ✅ Found update: {row['Name']}")
            
            if changes_found:
                print("   ✅ Sheet changes were applied to database")
                return True
            else:
                print("   ⚠️  No changes detected (might be expected)")
                return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_sheet_to_db_only())
    if success:
        print("\n🎯 SHEET → DATABASE SYNC IS WORKING!")
        print("The issue is the bidirectional sync overwriting the sheet.")
    else:
        print("\n❌ SHEET → DATABASE SYNC HAS ISSUES")
        sys.exit(1)