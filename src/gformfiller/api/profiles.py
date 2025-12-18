from fastapi import APIRouter, Request, HTTPException, status, Query
from typing import List, Dict
import logging

router = APIRouter(prefix="/gformfiller/profiles", tags=["Profiles"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Dict[str, str]])
async def list_profiles(request: Request):
    """List all available browser profiles."""
    fm = request.app.state.folder_manager
    profile_names = fm.list_profiles()
    profiles = []
    for profile_name in profile_names:
        profiles.append(
            {
                "name": profile_name,
                "created_at": fm._get_profile_date(profile_name)
            }
        )
    return profiles

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(request: Request, profile_name: str = Query(..., description="Name of the new profile")):
    """
    1. Initialize the profile directory.
    2. Launch the AuthWorker to handle Google login.
    """
    fm = request.app.state.folder_manager
    # We retrieve the AuthWorker from the app state
    auth_worker = request.app.state.auth_worker
    
    # Validation: Check if profile already exists
    if profile_name in fm.list_profiles():
        logger.warning(f"Creation failed: Profile '{profile_name}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Profile '{profile_name}' already exists."
        )
    
    try:
        # Launch the authentication process via the worker
        logger.info(f"Starting authentication worker for profile: {profile_name}")
        success = auth_worker.run(profile_name)
        
        if not success:
            # Cleanup if auth failed
            if profile_name in fm.list_profiles():
                fm.delete_profile(profile_name)
            raise Exception("Authentication worker returned failure.")

        return {
            "status": "success",
            "message": f"Profile '{profile_name}' created and authenticated."
        }
        
    except Exception as e:
        logger.error(f"Failed to create authenticated profile '{profile_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Profile creation/auth failed: {str(e)}"
        )

@router.delete("/{profile_name}/")
async def delete_profile(request: Request, profile_name: str):
    """Delete a specific browser profile."""
    fm = request.app.state.folder_manager
    
    if profile_name not in fm.list_profiles():
        raise HTTPException(status_code=404, detail="Profile not found")
        
    fm.delete_profile(profile_name)
    logger.info(f"Profile '{profile_name}' has been deleted.")
    return {"message": f"Profile '{profile_name}' deleted."}