#!/usr/bin/env python3
"""
MySQL setup script for Superjoin assignment
Creates database and initial configuration
"""
import asyncio
import sys
import os

def check_mysql_availability():
    """Check if MySQL is available"""
    print("🔍 Checking MySQL availability...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Try to connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='452003'
        )
        
        if connection.is_connected():
            print("✅ MySQL server is running and accessible")
            connection.close()
            return True
        else:
            print("❌ Cannot connect to MySQL server")
            return False
            
    except Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        print("\n🔧 Please ensure:")
        print("1. MySQL server is installed and running")
        print("2. Root password is set to 'password' (or update .env file)")
        print("3. MySQL service is started")
        return False
    except ImportError:
        print("❌ MySQL connector not installed")
        print("Run: pip install mysql-connector-python")
        return False

def create_mysql_database():
    """Create MySQL database if it doesn't exist"""
    print("🔧 Setting up MySQL database...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='452003'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS superjoin_sync")
            print("✅ Database 'superjoin_sync' created/verified")
            
            # Use the database
            cursor.execute("USE superjoin_sync")
            
            # Create a test table to verify connection
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_field VARCHAR(255)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Insert test data
            cursor.execute("INSERT INTO test_connection (test_field) VALUES ('MySQL connection working')")
            connection.commit()
            
            # Verify test data
            cursor.execute("SELECT * FROM test_connection")
            result = cursor.fetchone()
            if result:
                print("✅ MySQL connection test successful")
                
            # Clean up test table
            cursor.execute("DROP TABLE test_connection")
            connection.commit()
            
            print("✅ MySQL setup completed successfully!")
            return True
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

async def setup_application():
    """Setup application with MySQL"""
    print("\n🚀 Setting up Superjoin Sync with MySQL...")
    
    try:
        # Add current directory to Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.database import init_db, AsyncSessionLocal
        from app.sync import sync_service
        from sqlalchemy import select
        from app.models import SyncConfig
        
        # Initialize database
        print("📊 Initializing application database...")
        await init_db()
        print("✅ Application database initialized")
        
        # Create sample sync configuration
        print("⚙️ Creating sample sync configuration...")
        
        async with AsyncSessionLocal() as db:
            # Check if config already exists
            result = await db.execute(select(SyncConfig))
            existing_config = result.scalar_one_or_none()
            
            if existing_config:
                print(f"✅ Sync configuration already exists: {existing_config.id}")
                config = existing_config
            else:
                # Create new config
                config = await sync_service.create_sync(
                    db=db,
                    sheet_id="1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI",
                    sheet_name="Sheet1",
                    table_name="employees",
                    column_mapping={
                        "Name": "name",
                        "Email": "email", 
                        "Age": "age",
                        "City": "city"
                    }
                )
                print(f"✅ Created sync configuration: {config.id}")
        
        # Test initial sync
        print("🔄 Testing initial sync...")
        await sync_service._sync_sheet_to_db(config)
        print("✅ Initial Sheet→DB sync completed")
        
        await sync_service._sync_db_to_sheet(config)
        print("✅ Initial DB→Sheet sync completed")
        
        print("\n🎉 MySQL setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the backend: python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000 to access the dashboard")
        print("4. Use MySQL Workbench or phpMyAdmin to view/edit the database")
        
        print(f"\n📊 Configuration Details:")
        print(f"   Database: superjoin_sync")
        print(f"   Table: {config.table_name}")
        print(f"   Sheet ID: {config.sheet_id}")
        print(f"   Sheet Name: {config.sheet_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function"""
    print("🔍 SUPERJOIN ASSIGNMENT - MYSQL SETUP")
    print("="*50)
    
    # Step 1: Check MySQL availability
    if not check_mysql_availability():
        print("\n❌ MySQL is not available. Please install and start MySQL server.")
        print("\n📋 Installation Instructions:")
        print("Windows: Download from https://dev.mysql.com/downloads/installer/")
        print("macOS: brew install mysql && brew services start mysql")
        print("Linux: sudo apt install mysql-server")
        print("\nThen set root password to 'password' or update .env file")
        return False
    
    # Step 2: Create MySQL database
    mysql_success = create_mysql_database()
    
    if not mysql_success:
        print("\n❌ MySQL setup failed. Please check MySQL connection.")
        return False
    
    # Step 3: Setup application
    app_success = asyncio.run(setup_application())
    
    if app_success:
        print("\n✅ Complete setup successful!")
        print("Your Superjoin assignment is ready with MySQL!")
    else:
        print("\n❌ Application setup failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)