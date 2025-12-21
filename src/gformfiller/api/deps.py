# gformfiller/api/deps.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import logging


logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(request: Request, creds: HTTPAuthorizationCredentials = Depends(security)):
    auth = request.app.state.auth_manager
    user = auth.get_user_by_token(creds.credentials)
    if not user:
        logger.error("Unauthorized access attempt with invalid token.")
        raise HTTPException(status_code=403, detail="Invalid session or token.")
    return user["api_key"]