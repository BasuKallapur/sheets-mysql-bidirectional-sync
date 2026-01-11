import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SyncConfig
from app.sheets import SheetsService
from app.mysql import MySQLService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self):
        self.sheets = SheetsService()
        self.mysql = MySQLService()
        self.tasks = {}
        self.sync_interval = 10  # seconds
    
    async def create_sync(self, db: AsyncSession, sheet_id: str, sheet_name: str, table_name: str, column_mapping: dict):
        try:
            # Validate Google Sheet access
            sheet_data = await self.sheets.get_data(sheet_id, f"{sheet_name}!1:1")
            if not sheet_data:
                raise ValueError("Cannot access Google Sheet. Check sheet ID and permissions.")
            
            headers = sheet_data[0]
            logger.info(f"Found sheet headers: {headers}")
            
            # Create database table
            await self.mysql.create_table(table_name, headers)
            logger.info(f"Created/verified table: {table_name}")
            
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
            
            # Start sync task for real-time sync
            self.tasks[config.id] = asyncio.create_task(self._sync_loop(config.id))
            logger.info(f"Started sync loop for config {config.id}")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to create sync: {e}")
            raise
    
    async def _sync_loop(self, config_id: str):
        """Continuous sync loop for real-time updates"""
        logger.info(f"Starting sync loop for config {config_id}")
        
        while True:
            try:
                await self._do_sync(config_id)
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync loop error for {config_id}: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _do_sync(self, config_id: str):
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SyncConfig).where(SyncConfig.id == config_id))
            config = result.scalar_one_or_none()
            
            if not config or not config.is_active:
                return
            
            try:
                # BIDIRECTIONAL SYNC
                await self._sync_sheet_to_db(config)
                await asyncio.sleep(1)  # Small delay between operations
                await self._sync_db_to_sheet(config)
                
            except Exception as e:
                logger.error(f"Sync failed for config {config_id}: {e}")
    
    async def _sync_sheet_to_db(self, config):
        """Sync Google Sheet → Database with sheet_row_id mapping (NO MORE DUPLICATES)"""
        try:
            logger.info(f"Starting Sheet→DB sync for {config.table_name}")
            
            # Get sheet data with retry logic
            max_retries = 3
            sheet_data = None
            
            for attempt in range(max_retries):
                try:
                    sheet_data = await self.sheets.get_data(config.sheet_id, f"{config.sheet_name}!A:Z")
                    break
                except Exception as e:
                    logger.warning(f"Sheet access attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(2)
            
            if not sheet_data or len(sheet_data) <= 1:
                logger.info("No data rows found in sheet")
                return
            
            headers = sheet_data[0]
            rows = sheet_data[1:]
            
            # Convert sheet data to database format with sheet_row_id
            data_with_row_ids = []
            active_sheet_row_ids = []
            
            for i, row in enumerate(rows):
                try:
                    # Sheet row index starts from 2 (row 1 is header, row 2 is first data)
                    sheet_row_id = i + 2
                    
                    row_dict = {'sheet_row_id': sheet_row_id}
                    has_data = False
                    
                    for j, header in enumerate(headers):
                        # Skip the "Sheet Row Id" column - it's for display only
                        if header.lower().replace(' ', '_') == 'sheet_row_id':
                            continue
                            
                        db_column = config.column_mapping.get(header, header.lower().replace(' ', '_'))
                        value = row[j] if j < len(row) else ""
                        
                        # Clean and validate value
                        if isinstance(value, str):
                            value = value.strip()
                        
                        row_dict[db_column] = value
                        if value:  # Check if row has any data
                            has_data = True
                    
                    # Only include rows with actual data
                    if has_data:
                        data_with_row_ids.append(row_dict)
                        active_sheet_row_ids.append(sheet_row_id)
                        
                except Exception as e:
                    logger.warning(f"Skipping row {i + 2} due to error: {e}")
                    continue
            
            if data_with_row_ids:
                # Professional UPSERT using sheet_row_id
                await self.mysql.upsert_data_with_sheet_row_id(config.table_name, data_with_row_ids)
                logger.info(f"Sheet→DB: Synced {len(data_with_row_ids)} rows to {config.table_name}")
                
                # Optional: Clean up deleted rows (rows removed from sheet)
                await self.mysql.cleanup_deleted_sheet_rows(config.table_name, active_sheet_row_ids)
                logger.info(f"Sheet→DB: Cleaned up deleted rows")
            else:
                logger.info("No valid data to sync to database")
                
        except Exception as e:
            logger.error(f"Sheet→DB sync error: {e}")
            raise
    
    async def _sync_db_to_sheet(self, config):
        """Sync Database → Google Sheet (excludes internal id and sheet_row_id)"""
        try:
            logger.info(f"Starting DB→Sheet sync for {config.table_name}")
            
            # Get database data
            db_data = await self.mysql.get_all_data(config.table_name)
            
            if not db_data:
                logger.info("No data found in database")
                return
            
            # Convert to sheet format (exclude internal columns)
            headers = [col for col in db_data[0].keys() if col not in ['id', 'sheet_row_id']]
            
            # Create reverse mapping (db_column → sheet_column)
            reverse_mapping = {v: k for k, v in config.column_mapping.items()}
            
            # Map headers back to sheet column names
            sheet_headers = []
            for header in headers:
                sheet_header = reverse_mapping.get(header, header.replace('_', ' ').title())
                sheet_headers.append(sheet_header)
            
            # Convert data rows
            sheet_rows = [sheet_headers]  # Start with headers
            
            for row in db_data:
                sheet_row = []
                for header in headers:
                    value = row.get(header, '')
                    # Convert None to empty string
                    if value is None:
                        value = ''
                    sheet_row.append(str(value))
                sheet_rows.append(sheet_row)
            
            # Update Google Sheet with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.sheets.update_data(config.sheet_id, f"{config.sheet_name}!A:Z", sheet_rows)
                    logger.info(f"DB→Sheet: Synced {len(db_data)} rows to Google Sheet")
                    break
                except Exception as e:
                    logger.warning(f"Sheet update attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"DB→Sheet sync error: {e}")
            raise

sync_service = SyncService()