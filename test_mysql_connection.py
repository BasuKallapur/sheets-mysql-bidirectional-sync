#!/usr/bin/env python3
"""
Test MySQL connection for Superjoin assignment
"""
import mysql.connector
from mysql.connector import Error

def test_mysql_connection():
    """Test MySQL connection and basic operations"""
    print("🔍 Testing MySQL Connection...")
    
    try:
        # Test connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='superjoin_sync'
        )
        
        if connection.is_connected():
            print("✅ MySQL connection successful")
            
            cursor = connection.cursor()
            
            # Test database exists
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"✅ Connected to database: {db_name[0]}")
            
            # Show tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Test employees table if exists
            if any('employees' in str(table) for table in tables):
                cursor.execute("SELECT COUNT(*) FROM employees")
                count = cursor.fetchone()
                print(f"✅ Employees table has {count[0]} records")
                
                # Show sample data
                cursor.execute("SELECT * FROM employees LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    print("📊 Sample data:")
                    for row in rows:
                        print(f"   {row}")
            
            print("\n🎉 MySQL connection test completed successfully!")
            return True
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check username/password (default: root/password)")
        print("3. Run: python setup_mysql.py")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    test_mysql_connection()