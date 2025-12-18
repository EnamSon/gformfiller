# gformfiller/api/fillers.py

import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import (
    APIRouter, Request, HTTPException, status,
    Body, UploadFile, File, BackgroundTasks
)

router = APIRouter(prefix="/gformfiller/fillers", tags=["Fillers"])
logger = logging.getLogger(__name__)

# --- Filler Lifecycle ---

@router.get("/", response_model=List[str])
async def list_fillers(request: Request):
    """List all available fillers."""
    fm = request.app.state.folder_manager
    return fm.list_fillers()

@router.post("/{filler_name}/", status_code=status.HTTP_201_CREATED)
async def create_filler(request: Request, filler_name: str):
    """Initialize a new filler structure (folders + default JSON files)."""
    fm = request.app.state.folder_manager
    if filler_name in fm.list_fillers():
        raise HTTPException(status_code=400, detail="Filler already exists")
    
    try:
        fm.create_filler(filler_name)
        return {"message": f"Filler '{filler_name}' initialized successfully."}
    except Exception as e:
        logger.error(f"Error creating filler {filler_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filler_name}/")
async def delete_filler(request: Request, filler_name: str):
    """Delete a filler and all its associated data."""
    fm = request.app.state.folder_manager
    try:
        fm.delete_filler(filler_name)
        return {"message": f"Filler '{filler_name}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Filler not found or error: {e}")

# --- JSON Content Management ---

@router.get("/{filler_name}/{file_key}/", response_model=Dict[str, Any])
async def get_filler_file(request: Request, filler_name: str, file_key: str):
    """
    Retrieve content of a specific JSON file.
    Valid keys: 'config', 'formdata', 'metadata'
    """
    if file_key not in ["config", "formdata", "metadata"]:
        raise HTTPException(status_code=400, detail="Invalid file key. Use 'config', 'formdata' or 'metadata'.")
    
    fm = request.app.state.folder_manager
    try:
        return fm.get_filler_file_content(filler_name, file_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_key}.json not found for this filler.")

@router.put("/{filler_name}/{file_key}/")
async def update_filler_file(
    request: Request, 
    filler_name: str, 
    file_key: str, 
    data: Dict[str, Any] = Body(...)
):
    """
    Update a JSON file. 
    If updating 'formdata', it automatically resolves filenames to absolute paths.
    """
    if file_key not in ["config", "formdata", "metadata"]:
        raise HTTPException(status_code=400, detail="Invalid file key.")
    
    fm = request.app.state.folder_manager
    
    filler_path = fm.fillers_dir / filler_name
    if not filler_path.exists():
        logger.warning("Filler {filler_name} not found. Creating...")
        try:
            fm.create_filler(filler_name)
        except Exception as e:
            logger.error(f"Error creating filler {filler_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # --- Path resolution logic for FileUploadResponse ---
    if file_key == "formdata" and "FileUploadResponse" in data:
        files_base_path = fm.fillers_dir / filler_name / "files"
        
        for field, filename in data["FileUploadResponse"].items():
            if filename:
                absolute_path = files_base_path / filename
                data["FileUploadResponse"][field] = str(absolute_path)
                logger.debug(f"Resolved file path for {field}: {absolute_path}")

    try:
        fm.update_filler_file_content(filler_name, file_key, data)
        return {"message": f"{file_key}.json updated and paths resolved successfully."}
    except Exception as e:
        logger.error(f"Failed to update file {file_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- File Upload Management ---

@router.post("/{filler_name}/files/")
async def upload_filler_files(request: Request, filler_name: str, files: List[UploadFile] = File(...)):
    """
    Upload files (PDFs, Images, etc.) to the filler's 'files/' directory.
    These files can then be used by the AutomationWorker to fill upload fields.
    """
    fm = request.app.state.folder_manager
    uploaded_names = []
    
    try:
        # Resolve target directory
        target_dir = fm.fillers_dir / filler_name / "files"
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail="Filler directory structure not found.")

        for file in files:
            file_path = target_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(await file.read())
            uploaded_names.append(file.filename)
            
        return {"message": f"Uploaded {len(uploaded_names)} files.", "files": uploaded_names}
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")

# --- Execution Endpoint (Runner) ---

@router.post("/{filler_name}/run/", status_code=status.HTTP_202_ACCEPTED)
async def run_filler(
    filler_name: str, 
    request: Request,
    background_tasks: BackgroundTasks,
    form_data_override: Optional[Dict[str, Any]] = Body(None)
):
    fm = request.app.state.folder_manager
    worker = request.app.state.automation_worker

    # 1. Vérification de l'existence du filler
    if filler_name not in fm.list_fillers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Filler '{filler_name}' introuvable."
        )

    # 2. Préparation des données (Priorité : Override > Local)
    final_form_data = form_data_override
    
    if final_form_data is None:
        try:
            # On récupère les données locales si aucun override n'est fourni
            final_form_data = fm.get_filler_file_content(filler_name, "formdata")
            logger.info(f"Using local formdata.json for {filler_name}")
        except FileNotFoundError:
            logger.warning(f"No local formdata found for {filler_name}, starting with empty data.")
            final_form_data = {}

    # 3. Résolution des chemins de fichiers (FileUploadResponse)
    # On s'assure que même les données envoyées via override ont des chemins absolus
    if "FileUploadResponse" in final_form_data:
        files_base_path = fm.fillers_dir / filler_name / "files"
        for field, filename in final_form_data["FileUploadResponse"].items():
            if filename and not os.path.isabs(str(filename)):
                final_form_data["FileUploadResponse"][field] = str(files_base_path / filename)

    # 4. Ajout à la file d'attente des tâches de fond
    try:
        logger.info(f"Enqueuing automation for '{filler_name}'")

        background_tasks.add_task(
            worker.run, 
            filler_name=filler_name, 
            form_data=final_form_data # On passe les données prêtes à l'emploi
        )

        return {
            "status": "accepted",
            "message": f"Automation for '{filler_name}' started. Monitoring available at /status.",
            "filler": filler_name
        }

    except Exception as e:
        logger.exception(f"Failed to queue background task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not start background task."
        )

@router.get("/{filler_name}/status")
async def get_filler_status(request: Request, filler_name: str):
    """
    Retrieve the current execution status from metadata.
    Essential when using background tasks to know when the work is done.
    """
    fm = request.app.state.folder_manager
    try:
        metadata = fm.get_filler_file_content(filler_name, "metadata")
        return {
            "filler": filler_name,
            "status": metadata.get("status", "unknown"),
            "last_update": metadata.get("updated_at", "N/A")
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Status file not found.")