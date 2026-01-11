#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')

from app.mysql import MySQLService

async def check_database():
    mysql = MySQLService()
    
    try:
        data = await mysql.get_all_data('employees')
        print(f"📊 Database has {len(data)} rows:")
        
        for i, row in enumerate(data[:5]):  # Show first 5 rows
            print(f"  Row {i+1}: {dict(row)}")
            
        if len(data) > 5:
            print(f"  ... and {len(data) - 5} more rows")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())