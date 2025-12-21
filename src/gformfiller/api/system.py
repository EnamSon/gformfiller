# gformfiller/api/system.py

from .deps import get_current_user
from fastapi import APIRouter, Request, HTTPException, Body, Depends
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/gformfiller", tags=["System"])
logger = logging.getLogger(__name__)

# --- Configuration par défaut ---

@router.get("/default/", response_model=Dict[str, Any])
async def get_default_config(request: Request):
    """
    Retrieve the global default configuration used for new fillers.
    """
    cm = request.app.state.config_manager
    try:
        return cm.get_default_config()
    except Exception as e:
        logger.error(f"Failed to load default config: {e}")
        raise HTTPException(status_code=500, detail="Error loading default configuration.")

@router.put("/default/")
async def update_default_config(request: Request, data: Dict[str, Any] = Body(...)):
    """
    Update the global default configuration (default.json).
    """
    cm = request.app.state.config_manager
    try:
        cm.update_default_config(data)
        return {"message": "Global default configuration updated successfully."}
    except Exception as e:
        logger.error(f"Failed to update default config: {e}")
        raise HTTPException(status_code=500, detail="Error updating default configuration.")

# --- Journaux système (Logs) ---

@router.get("/log/", response_model=List[Dict[str, Any]])
async def get_system_logs(
    request: Request,
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """
    Fetch the latest logs from the SQLite log database.
    """
    fm = request.app.state.folder_manager
    db_logger = fm.get_db_logger(current_user)
    # We assume FolderManager provides access to the DB logger's fetch method
    try:
        # If your FolderManager has a reference to the db_logger:
        logs = db_logger.get_logs(limit=limit)
        return logs

    except AttributeError:
        # Fallback if the method isn't implemented yet in FolderManager
        logger.error("DB Logger access not implemented in FolderManager.")
        raise HTTPException(status_code=501, detail="Log retrieval not implemented.")

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch logs from database.")