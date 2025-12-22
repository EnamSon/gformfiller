# gformfiller/api/auth.py

from .deps import get_current_user
from fastapi import (
    APIRouter, Request, HTTPException, Form, status, Depends,Security
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from gformfiller.infrastructure.folder_manager.constants import USERS_DB
import logging
import sqlite3

router = APIRouter(prefix="/gformfiller/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    """Create a new user and initialize their private workspace."""
    auth = request.app.state.auth_manager
    fm = request.app.state.folder_manager
    
    api_key = auth.create_user(username, password)
    if not api_key:
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    # Pre-create user directory structure
    try:
        fm.get_user_path(username)
        logger.info(f"Workspace initialized for new user: {username}")
    except Exception as e:
        logger.error(f"Failed to init workspace for {username}: {e}")

    return {"message": "User created successfully", "access_token": api_key}

@router.post("/signin/")
async def signin(request: Request, username: str = Form(...), password: str = Form(...)):
    """Authenticate user and return their access token (API Key)."""
    auth = request.app.state.auth_manager
    api_key = auth.verify_user(username, password)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password."
        )
    
    return {
        "access_token": api_key,
        "token_type": "bearer",
        "username": username
    }

@router.get("/me/")
async def get_me(request: Request, current_user: str = Depends(get_current_user)):
    return {
        'username': current_user
    }