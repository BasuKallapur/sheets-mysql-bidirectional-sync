from sqlalchemy import text
from app.database import engine

class MySQLService:
    async def create_table(self, table_name: str, headers: list):
        columns = ", ".join([f"`{header}` TEXT" for header in headers])
        query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {columns}
            )
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
        
        # Clear table
        async with engine.begin() as conn:
            await conn.execute(text(f"DELETE FROM `{table_name}` WHERE id > 0"))
            
            # Insert new data
            columns = list(data[0].keys())
            placeholders = [f":{col}" for col in columns]
            query = f"""
                INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])})
                VALUES ({', '.join(placeholders)})
            """
            await conn.execute(text(query), data)