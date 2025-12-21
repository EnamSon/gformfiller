from fastapi import FastAPI
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager
from gformfiller.infrastructure.notif_manager import NotifManager
from gformfiller.infrastructure.auth_manager import AuthManager
from gformfiller.core.auth_worker import AuthWorker
from gformfiller.core.filler_worker import FillerWorker
from gformfiller.api.profiles import router as profiles_router
from gformfiller.api.fillers import router as fillers_router
from gformfiller.api.system import router as system_router
from gformfiller.api.inscriptions import router as inscriptions_router
from gformfiller.api.notifications import router as notifications_router
from gformfiller.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

import logging
import argparse
import uvicorn

def create_app() -> FastAPI:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    app = FastAPI(title="GFormFiller API", redirect_slashes=True)

    # 1. Initialize Infrastructure
    folder_manager = FolderManager()
    config_manager = ConfigManager(folder_manager)
    notif_manager = NotifManager(folder_manager)
    auth_manager = AuthManager(folder_manager)

    # 2. Initialize Workers
    auth_worker = AuthWorker(folder_manager, config_manager)
    automation_worker = FillerWorker(folder_manager, config_manager, notif_manager)

    # 3. Inject into app state for route access
    app.state.folder_manager = folder_manager
    app.state.config_manager = config_manager
    app.state.notif_manager = notif_manager
    app.state.auth_manager = auth_manager
    app.state.auth_worker = auth_worker
    app.state.automation_worker = automation_worker

    # 4. Include Routers
    app.include_router(profiles_router)
    app.include_router(fillers_router)
    app.include_router(system_router)
    app.include_router(inscriptions_router)
    app.include_router(notifications_router)
    app.include_router(auth_router)

    return app

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    app = create_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    run()