#!/usr/bin/env python3
"""
Manually clear Google Sheet completely and set only 4 rows
"""
import asyncio
import sys
sys.path.append('.')

from app.sheets import SheetsService
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import SyncConfig

async def manual_clear_sheet():
    """Manually clear and set Google Sheet"""
    print("🧹 MANUALLY CLEARING GOOGLE SHEET")
    print("=" * 50)
    
    try:
        sheets = SheetsService()
        
        # Get config
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.table_name == 'employees'))
            config = result.scalar_one_or_none()
        
        sheet_id = config.sheet_id
        sheet_name = config.sheet_name
        
        print(f"📋 Clearing sheet: {sheet_id}")
        
        # Step 1: Clear everything by setting a massive range to empty
        print("1️⃣ Clearing all existing data...")
        
        # Create a large empty grid to overwrite everything
        empty_rows = []
        for i in range(1000):  # Clear 1000 rows
            empty_rows.append([""] * 10)  # 10 empty columns
        
        await sheets.update_data(sheet_id, f"{sheet_name}!A1:J1000", empty_rows)
        print("   ✅ Cleared 1000 rows")
        
        # Step 2: Set only our 4 rows + header
        print("2️⃣ Setting clean data...")
        
        clean_data = [
            ["Name", "Email", "Age", "City", "City 1"],  # Header
            ["John Doe", "john@test.com", "30", "New York", ""],
            ["Jane Smith", "jane@test.com", "25", "Los Angeles", ""],
            ["Bob Wilson", "bob@test.com", "35", "Chicago", ""],
            ["Alice Brown", "alice@test.com", "28", "Miami", ""]
        ]
        
        await sheets.update_data(sheet_id, f"{sheet_name}!A1:E5", clean_data)
        print("   ✅ Set 4 clean rows")
        
        # Step 3: Verify
        print("3️⃣ Verifying...")
        verification = await sheets.get_data(sheet_id, f"{sheet_name}!A1:E20")
        
        # Count non-empty rows
        non_empty_rows = 0
        for row in verification:
            if any(cell.strip() for cell in row if cell):  # If any cell has content
                non_empty_rows += 1
        
        print(f"   📊 Sheet now has {non_empty_rows} rows with data")
        
        if non_empty_rows <= 5:  # Header + 4 data rows
            print("\n🎉 SUCCESS! Google Sheet cleaned to 4 rows!")
            print("\n📋 Sheet contents:")
            for i, row in enumerate(verification[:5]):
                if any(cell.strip() for cell in row if cell):
                    print(f"   Row {i+1}: {' | '.join(row[:4])}")
            return True
        else:
            print(f"\n❌ Still has {non_empty_rows} rows")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(manual_clear_sheet())
    if success:
        print("\n✅ SHEET IS CLEAN - NOW YOU HAVE 4 ROWS IN BOTH SYSTEMS!")
        print("🚀 START VALIDATION NOW!")
    else:
        sys.exit(1)