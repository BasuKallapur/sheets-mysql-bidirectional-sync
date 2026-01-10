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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)