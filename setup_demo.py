#!/usr/bin/env python3
"""
Setup script for Superjoin Sync Demo
Creates sample sync configuration and initializes the system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, AsyncSessionLocal
from app.sync import sync_service

async def setup_demo():
    print("🚀 Setting up Superjoin Sync Demo...")
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_db()
        print("✅ Database initialized")
        
        # Create sample sync configuration
        print("⚙️ Creating sample sync configuration...")
        
        async with AsyncSessionLocal() as db:
            # Check if config already exists
            from sqlalchemy import select
            from app.models import SyncConfig
            
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
        
        print("\n🎉 Demo setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the backend: python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000 to access the dashboard")
        print("4. Use DB Browser for SQLite to view/edit the database")
        print("5. Edit the Google Sheet to test real-time sync")
        
        print(f"\n📊 Configuration Details:")
        print(f"   Sheet ID: {config.sheet_id}")
        print(f"   Sheet Name: {config.sheet_name}")
        print(f"   Table Name: {config.table_name}")
        print(f"   Database File: superjoin_sync.db")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(setup_demo())
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)