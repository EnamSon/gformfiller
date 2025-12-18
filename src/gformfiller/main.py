from fastapi import FastAPI
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager
from gformfiller.core.auth_worker import AuthWorker
from gformfiller.core.filler_worker import FillerWorker
from gformfiller.api.profiles import router as profiles_router
from gformfiller.api.fillers import router as fillers_router
from gformfiller.api.system import router as system_router
import logging


def create_app() -> FastAPI:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    app = FastAPI(title="GFormFiller API")

    # 1. Initialize Infrastructure
    folder_manager = FolderManager()
    config_manager = ConfigManager(folder_manager)

    # 2. Initialize Workers
    auth_worker = AuthWorker(folder_manager, config_manager)
    automation_worker = FillerWorker(folder_manager, config_manager)

    # 3. Inject into app state for route access
    app.state.folder_manager = folder_manager
    app.state.config_manager = config_manager
    app.state.auth_worker = auth_worker
    app.state.automation_worker = automation_worker

    # 4. Include Routers
    app.include_router(profiles_router)
    app.include_router(fillers_router)
    app.include_router(system_router)

    return app

app = create_app()