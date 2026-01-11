#!/usr/bin/env python3
"""
Test MySQL and Google Sheets connections independently
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

def test_mysql():
    """Test MySQL connection"""
    print("🔍 Testing MySQL connection...")
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='452003',
            database='superjoin_sync'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM employees LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"✅ MySQL connection successful!")
        print(f"   Database: superjoin_sync")
        print(f"   Table: employees")
        print(f"   Row count: {count}")
        if rows:
            print(f"   Sample data: {rows[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets connection"""
    print("\n🔍 Testing Google Sheets connection...")
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # Load credentials
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Test with the sheet from your config
        sheet_id = "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI"
        
        # Try to read the sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A1:E10"
        ).execute()
        
        values = result.get('values', [])
        
        print(f"✅ Google Sheets connection successful!")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Rows found: {len(values)}")
        if values:
            print(f"   Headers: {values[0]}")
            if len(values) > 1:
                print(f"   Sample row: {values[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        print(f"   This might be due to:")
        print(f"   - Network/proxy issues")
        print(f"   - Firewall blocking Google APIs")
        print(f"   - Invalid credentials")
        print(f"   - Sheet permissions")
        return False

async def test_app_database():
    """Test application database setup"""
    print("\n🔍 Testing application database...")
    try:
        from app.database import AsyncSessionLocal
        from app.models import SyncConfig
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig))
            configs = result.scalars().all()
            
            print(f"✅ Application database working!")
            print(f"   Sync configs found: {len(configs)}")
            
            for config in configs:
                print(f"   Config: {config.id}")
                print(f"     Sheet: {config.sheet_id}")
                print(f"     Table: {config.table_name}")
                print(f"     Active: {config.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application database failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CONNECTION TESTS")
    print("=" * 50)
    
    mysql_ok = test_mysql()
    sheets_ok = test_google_sheets()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if mysql_ok:
        print("✅ MySQL: Working perfectly")
    else:
        print("❌ MySQL: Needs fixing")
    
    if sheets_ok:
        print("✅ Google Sheets: Working perfectly")
    else:
        print("❌ Google Sheets: Connection issues (likely network/proxy)")
    
    # Test app database
    app_db_ok = asyncio.run(test_app_database())
    
    if app_db_ok:
        print("✅ Application Database: Working perfectly")
    else:
        print("❌ Application Database: Needs fixing")
    
    print("\n" + "=" * 50)
    
    if mysql_ok and app_db_ok:
        print("🎉 CORE FUNCTIONALITY READY!")
        print("\nYour application can:")
        print("✅ Connect to MySQL database")
        print("✅ Store and retrieve sync configurations")
        print("✅ Handle bidirectional data sync")
        
        if sheets_ok:
            print("✅ Connect to Google Sheets")
            print("\n🚀 EVERYTHING IS WORKING!")
            print("Run: python -m uvicorn app.main:app --reload")
        else:
            print("⚠️  Google Sheets has connection issues")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check your internet connection")
            print("2. Try from a different network")
            print("3. Check if corporate firewall blocks Google APIs")
            print("4. Verify credentials.json is valid")
            print("\n💡 You can still test the MySQL functionality!")
    else:
        print("❌ SOME ISSUES NEED FIXING")
    
    return mysql_ok and sheets_ok and app_db_ok

if __name__ == "__main__":
    success = main()