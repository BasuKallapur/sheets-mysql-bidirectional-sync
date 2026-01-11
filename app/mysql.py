from sqlalchemy import text
from app.database import engine

class MySQLService:
    async def create_table(self, table_name: str, headers: list):
        # Remove duplicates and clean headers
        unique_headers = []
        seen = set()
        for header in headers:
            clean_header = str(header).strip()
            if not clean_header:
                continue
            
            # Handle duplicates by adding a suffix
            original_header = clean_header
            counter = 1
            while clean_header in seen:
                clean_header = f"{original_header}_{counter}"
                counter += 1
            
            unique_headers.append(clean_header)
            seen.add(clean_header)
        
        # Create table with proper MySQL syntax + sheet_row_id for sync mapping
        columns = ", ".join([f"`{header}` TEXT" for header in unique_headers])
        query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sheet_row_id INT UNIQUE NOT NULL,
                {columns},
                UNIQUE KEY unique_sheet_row (sheet_row_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        async with engine.begin() as conn:
            await conn.execute(text(query))
    
    async def get_data(self, table_name: str):
        query = f"SELECT * FROM `{table_name}`"
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_all_data(self, table_name: str):
        """Get all data from a table"""
        query = f"SELECT * FROM `{table_name}` ORDER BY id"
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    async def clear_and_insert(self, table_name: str, data: list):
        if not data:
            return
        
        async with engine.begin() as conn:
            # Clear table
            await conn.execute(text(f"DELETE FROM `{table_name}`"))
            
            # Reset auto-increment counter for MySQL
            await conn.execute(text(f"ALTER TABLE `{table_name}` AUTO_INCREMENT = 1"))
            
            # Insert new data (exclude 'id' column to let auto-increment work)
            columns = [col for col in data[0].keys() if col != 'id']
            if not columns:
                return
                
            placeholders = [f":{col}" for col in columns]
            query = f"""
                INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])})
                VALUES ({', '.join(placeholders)})
            """
            
            # Prepare data without 'id' column
            clean_data = []
            for row in data:
                clean_row = {col: row[col] for col in columns if col in row}
                clean_data.append(clean_row)
            
            if clean_data:
                await conn.execute(text(query), clean_data)
    
    async def upsert_data_with_sheet_row_id(self, table_name: str, data_with_row_ids: list):
        """
        Professional UPSERT using sheet_row_id as deterministic identifier
        data_with_row_ids: [{'sheet_row_id': 2, 'Name': 'John', 'Email': 'john@test.com', ...}, ...]
        """
        if not data_with_row_ids:
            return
        
        async with engine.begin() as conn:
            for row_data in data_with_row_ids:
                if 'sheet_row_id' not in row_data:
                    continue
                
                # Separate sheet_row_id from other columns
                sheet_row_id = row_data['sheet_row_id']
                columns = [col for col in row_data.keys() if col not in ['id', 'sheet_row_id']]
                
                if not columns:
                    continue
                
                # Build INSERT ... ON DUPLICATE KEY UPDATE query
                column_list = ['sheet_row_id'] + columns
                placeholders = [':sheet_row_id'] + [f':{col}' for col in columns]
                update_clause = ", ".join([f"`{col}` = VALUES(`{col}`)" for col in columns])
                
                query = f"""
                    INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in column_list])})
                    VALUES ({', '.join(placeholders)})
                    ON DUPLICATE KEY UPDATE {update_clause}
                """
                
                # Prepare data for query
                query_data = {'sheet_row_id': sheet_row_id}
                for col in columns:
                    query_data[col] = row_data.get(col, '')
                
                await conn.execute(text(query), query_data)
    
    async def cleanup_deleted_sheet_rows(self, table_name: str, active_sheet_row_ids: list):
        """
        Remove database rows whose sheet_row_id no longer exist in the sheet
        This handles deletions in Google Sheet
        """
        if not active_sheet_row_ids:
            return
        
        async with engine.begin() as conn:
            # Convert to comma-separated string for SQL IN clause
            id_list = ','.join(map(str, active_sheet_row_ids))
            query = f"DELETE FROM `{table_name}` WHERE sheet_row_id NOT IN ({id_list})"
            await conn.execute(text(query))
    
    async def create_unique_index(self, table_name: str, column: str):
        """Create unique index for upsert operations"""
        try:
            query = f"CREATE UNIQUE INDEX idx_{table_name}_{column} ON `{table_name}` (`{column}`)"
            async with engine.begin() as conn:
                await conn.execute(text(query))
        except Exception:
            # Index might already exist, ignore error
            pass