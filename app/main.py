import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

@app.post("/apps-script-sync")
async def apps_script_sync(request: dict, db: AsyncSession = Depends(get_db)):
    """Handle sync requests from Google Apps Script"""
    try:
        sheet_id = request.get("sheet_id")
        edit_info = request.get("edit_info", {})
        trigger_source = request.get("trigger_source", "apps_script")
        
        # Find matching sync config
        result = await db.execute(select(SyncConfig).where(SyncConfig.sheet_id == sheet_id))
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail=f"No sync config found for sheet {sheet_id}")
        
        # Log the Apps Script trigger
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Apps Script sync triggered: {edit_info}")
        
        # Determine sync direction based on edit type
        edit_type = edit_info.get("editType", "EDIT")
        
        if edit_type in ["EDIT", "STRUCTURE_CHANGE"]:
            # Sheet was edited, sync Sheet → DB first, then DB → Sheet for consistency
            await sync_service._sync_sheet_to_db(config)
            # Small delay to ensure consistency
            import asyncio
            await asyncio.sleep(0.5)
            await sync_service._sync_db_to_sheet(config)
            
        elif edit_type == "MANUAL":
            # Manual trigger, do full bidirectional sync
            await sync_service._sync_sheet_to_db(config)
            await asyncio.sleep(0.5)
            await sync_service._sync_db_to_sheet(config)
        
        return {
            "message": "Apps Script sync completed successfully",
            "config_id": config.id,
            "edit_info": edit_info,
            "sync_direction": "bidirectional",
            "timestamp": request.get("timestamp")
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Apps Script sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for Apps Script testing"""
    return {
        "status": "healthy",
        "service": "Superjoin Sync API",
        "timestamp": "2024-01-12T00:00:00Z",
        "apps_script_ready": True
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)