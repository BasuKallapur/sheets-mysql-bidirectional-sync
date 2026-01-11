from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict

from app.database import init_db, get_db
from app.models import SyncConfig
from app.sync import sync_service

class SyncConfigCreate(BaseModel):
    sheet_id: str
    sheet_name: str
    table_name: str
    column_mapping: Dict[str, str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Superjoin Sync MVP", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Superjoin Sync MVP is running"}

@app.post("/sync")
async def create_sync(config: SyncConfigCreate, db: AsyncSession = Depends(get_db)):
    try:
        sync_config = await sync_service.create_sync(
            db, config.sheet_id, config.sheet_name, config.table_name, config.column_mapping
        )
        return {"id": sync_config.id, "message": "Sync created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync")
async def list_syncs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SyncConfig))
    configs = result.scalars().all()
    return [
        {
            "id": config.id,
            "sheet_id": config.sheet_id,
            "sheet_name": config.sheet_name,
            "table_name": config.table_name,
            "is_active": config.is_active,
            "created_at": config.created_at
        }
        for config in configs
    ]

@app.post("/manual-sync")
async def manual_sync(db: AsyncSession = Depends(get_db)):
    """Trigger manual sync for all configurations"""
    try:
        result = await db.execute(select(SyncConfig))
        configs = result.scalars().all()
        
        sync_results = []
        for config in configs:
            try:
                # Trigger both directions of sync
                await sync_service._sync_sheet_to_db(config)
                await sync_service._sync_db_to_sheet(config)
                sync_results.append({"config_id": config.id, "status": "success"})
            except Exception as e:
                sync_results.append({"config_id": config.id, "status": "error", "error": str(e)})
        
        return {"message": "Manual sync completed", "results": sync_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-sheet-to-db")
async def sync_sheet_to_db(db: AsyncSession = Depends(get_db)):
    """Sync Google Sheet → Database only"""
    try:
        result = await db.execute(select(SyncConfig))
        configs = result.scalars().all()
        
        sync_results = []
        for config in configs:
            try:
                await sync_service._sync_sheet_to_db(config)
                sync_results.append({"config_id": config.id, "status": "success", "direction": "Sheet → DB"})
            except Exception as e:
                sync_results.append({"config_id": config.id, "status": "error", "error": str(e)})
        
        return {"message": "Sheet → Database sync completed", "results": sync_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-db-to-sheet")
async def sync_db_to_sheet(db: AsyncSession = Depends(get_db)):
    """Sync Database → Google Sheet only"""
    try:
        result = await db.execute(select(SyncConfig))
        configs = result.scalars().all()
        
        sync_results = []
        for config in configs:
            try:
                await sync_service._sync_db_to_sheet(config)
                sync_results.append({"config_id": config.id, "status": "success", "direction": "DB → Sheet"})
            except Exception as e:
                sync_results.append({"config_id": config.id, "status": "error", "error": str(e)})
        
        return {"message": "Database → Sheet sync completed", "results": sync_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)