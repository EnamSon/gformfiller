# gformfiller/api/inscriptions.py

import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import (
    APIRouter, Request, HTTPException,
    Body, UploadFile, File, BackgroundTasks
)

router = APIRouter(prefix="/gformfiller/inscriptions", tags=["Inscriptions"])
logger = logging.getLogger(__name__)


# --- routes spécifique au projet TCFFormFiller ---

@router.get("/", response_model=List[Dict[str, str]])
async def list_inscriptions(request: Request):
    fm = request.app.state.folder_manager
    all_form_data = fm.get_all_form_data()
    all_metadata = fm.get_all_metadata()
    infos = []

    for filler_name in all_form_data:
        full_name = ""
        try:
            full_name = all_form_data[filler_name]["TextResponse"].get(
                "nom < complet", filler_name.replace("_", " ")
            )
        except Exception as e:
            logger.error(f"Can't extract the fullname for reason: {e}")

        phone = ""
        try:
            phone = all_form_data[filler_name]["TextResponse"].get("phone", "")
        except Exception as e:
            logger.error(f"Can't extract phone number for reason: {e}")

        status = all_metadata[filler_name].get("status", "unknown")
        date = all_metadata[filler_name].get("created_at", "")

        infos.append({
            "id": filler_name,
            "full_name": full_name,
            "phone": phone,
            "status": status,
            "date": date
        })

    return infos


@router.get("/pending/count/", response_model=int)
async def pending_inscriptions_count(request: Request):
    fm = request.app.state.folder_manager
    all_metadata = fm.get_all_metadata()
    return sum(1 for filler_name in all_metadata if all_metadata[filler_name].get("status") == "pending")


@router.get("/status/", response_model=Dict[str, int])
async def status(request: Request):
    fm = request.app.state.folder_manager
    all_metadata = fm.get_all_metadata()
    total = len(all_metadata)
    pending = 0
    failed = 0
    completed = 0
    for metadata in all_metadata.values():
        status = metadata.get("status")
        if status == "pending":
            pending += 1
        elif status == "completed":
            completed += 1
        else:
            failed += 1

    return {
        "total": total,
        "pending": pending,
        "failed": failed,
        "completed": completed
    }