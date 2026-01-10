import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SyncConfig
from app.sheets import SheetsService
from app.mysql import MySQLService

class SyncService:
    def __init__(self):
        self.sheets = SheetsService()
        self.mysql = MySQLService()
        self.tasks = {}
    
    async def create_sync(self, db: AsyncSession, sheet_id: str, sheet_name: str, table_name: str, column_mapping: dict):
        # Get sheet headers to create table
        sheet_data = await self.sheets.get_data(sheet_id, f"{sheet_name}!1:1")
        if sheet_data:
            headers = sheet_data[0]
            await self.mysql.create_table(table_name, headers)
        
        # Save config
        config = SyncConfig(
            sheet_id=sheet_id,
            sheet_name=sheet_name,
            table_name=table_name,
            column_mapping=column_mapping
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        # Start sync task
        self.tasks[config.id] = asyncio.create_task(self._sync_loop(config.id))
        return config
    
    async def _sync_loop(self, config_id: str):
        while True:
            try:
                await self._do_sync(config_id)
                await asyncio.sleep(5)  # Sync every 5 seconds
            except Exception as e:
                print(f"Sync error: {e}")
                await asyncio.sleep(10)
    
    async def _do_sync(self, config_id: str):
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.id == config_id))
            config = result.scalar_one_or_none()
            
            if not config:
                return
            
            # BIDIRECTIONAL SYNC
            await self._sync_sheet_to_db(config)
            await self._sync_db_to_sheet(config)
    
    async def _sync_sheet_to_db(self, config):
        """Sync Google Sheet → Database"""
        # Get sheet data
        sheet_data = await self.sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:Z")
        
        if len(sheet_data) > 1:  # Has headers + data
            headers = sheet_data[0]
            rows = sheet_data[1:]
            
            # Convert to dict format
            data_dicts = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        db_column = config.column_mapping.get(header, header)
                        row_dict[db_column] = row[i]
                    else:
                        # Fill missing columns with empty string
                        db_column = config.column_mapping.get(header, header)
                        row_dict[db_column] = ""
                
                # Only add rows that have at least a name
                if row_dict.get('name', '').strip():
                    data_dicts.append(row_dict)
            
            # Update database
            if data_dicts:
                await self.mysql.clear_and_insert(config.table_name, data_dicts)
                print(f"Sheet→DB: Synced {len(data_dicts)} rows to {config.table_name}")
    
    async def _sync_db_to_sheet(self, config):
        """Sync Database → Google Sheet"""
        try:
            # Get database data
            db_data = await self.mysql.get_all_data(config.table_name)
            
            if db_data:
                # Convert to sheet format
                headers = list(db_data[0].keys())
                
                # Create reverse mapping (db_column → sheet_column)
                reverse_mapping = {v: k for k, v in config.column_mapping.items()}
                
                # Map headers back to sheet column names
                sheet_headers = [reverse_mapping.get(h, h) for h in headers]
                
                # Convert data rows
                sheet_rows = [sheet_headers]  # Start with headers
                for row in db_data:
                    sheet_row = [str(row.get(h, '')) for h in headers]
                    sheet_rows.append(sheet_row)
                
                # Update Google Sheet
                await self.sheets.update_data(config.sheet_id, f"{config.sheet_name}!A:Z", sheet_rows)
                print(f"DB→Sheet: Synced {len(db_data)} rows to Google Sheet")
                
        except Exception as e:
            print(f"DB→Sheet sync error: {e}")

sync_service = SyncService()