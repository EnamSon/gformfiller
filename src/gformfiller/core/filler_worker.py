# gformfiller/core/filler_worker

import logging
import os
import subprocess
import socket
import random
from datetime import datetime
from typing import Dict, Any, Optional

from .constants import Status
from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager
from gformfiller.infrastructure.notif_manager import NotifManager
from gformfiller.infrastructure.driver import get_chromedriver, quit_chromedriver
from gformfiller.domain.form_filler import FormFiller
from gformfiller.domain.ai import create_ai_client
from gformfiller.infrastructure.folder_manager.constants import (
    LOCK_FILE,
    FileKeys,
    CHROMEDRIVER_DIR,
    CHROME_BIN_DIR,
    RECORD_SUBDIR,
    SCREENSHOTS_SUBDIR,
    PDFS_SUBDIR
)

logger = logging.getLogger(__name__)


def _launch_chrome_remote_debug(user_data_dir: str, binary_loc: str, port: int = 9222):
    args = [
        binary_loc,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}"
    ]
    subprocess.Popen(args)


class FillerWorker:
    def __init__(self, folder_manager: FolderManager, config_manager: ConfigManager, notif_manager: NotifManager):
        self.fm = folder_manager
        self.cm = config_manager
        self.nm = notif_manager

    def is_profile_locked(self, profile_name: str) -> bool:
        lock_file = self.fm.profiles_dir / profile_name / LOCK_FILE
        return lock_file.exists()

    def run(self, user_id: str, filler_name: str, form_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exécute le cycle d'automatisation.
        :param filler_name: Nom du filler cible.
        :param form_data: Données de formulaire optionnelles (écrase le contenu de formdata.json).
        """
        # 1. Résolution de la configuration et des métadonnées
        config = self.cm.get_resolved_config(user_id, filler_name)
        metadata = self.fm.get_filler_file_content(user_id, filler_name, FileKeys.METADATA)
        
        # Si form_data n'est pas passé en paramètre, on le charge depuis le fichier local
        if form_data is None:
            form_data = self.fm.get_filler_file_content(user_id, filler_name, FileKeys.FORMDATA)

        if not metadata.get("url"):
            logger.error(f"URL absente pour le filler: {filler_name}")
            return False

        # 2. Préparation du Driver
        user_paths = self.fm.get_user_paths(user_id)
        driver_path = str(self.fm.root / CHROMEDRIVER_DIR / "chromedriver")
        binary_loc = str(self.fm.root / CHROME_BIN_DIR / "chrome")
        profile_path = str(self.fm.profiles_dir / config.profile)
        lock_file = self.fm.profiles_dir / config.profile / LOCK_FILE

        if self.is_profile_locked(config.profile):
            logger.error(f"Profile {config.profile} is locked. Another instance is running.")
            return False

        driver = get_chromedriver(
            driver_path=driver_path,
            binary_location=binary_loc,
            user_data_dir=profile_path,
            headless=config.headless,
            remote=config.remote,
            no_sandbox=True,
            disable_images=True,
            disable_gpu=True,
            disable_dev_shm=True,
            window_size="1920,1080"
        )

        try:
            lock_file.touch()

            # 3. Gestion de l'IA conditionnelle
            ai_client = None
            driver.get(metadata["url"])
            # 4. Initialisation du moteur FormFiller
            filler_paths = self.fm.get_filler_paths(user_id, filler_name)
            filler_engine = FormFiller(
                driver=driver,
                form_data=form_data,
                screenshots_dir=str(filler_paths[RECORD_SUBDIR] / SCREENSHOTS_SUBDIR),
                output_dir=str(filler_paths[RECORD_SUBDIR] / PDFS_SUBDIR),
                submit=config.submit,
                max_retries=config.max_retries
            )

            # 5. Exécution
            success = filler_engine.run()
            
            # Mise à jour de l'état
            metadata["status"] = Status.COMPLETED if success else Status.FAILED

            return success

        except Exception as e:
            logger.exception(f"Erreur critique lors de l'exécution de '{filler_name}': {e}")
            metadata["status"] = Status.ERROR

            return False
            
        finally:
            metadata["last_access"] = datetime.now().isoformat()
            self.fm.update_filler_file_content(user_id, filler_name, FileKeys.METADATA, metadata)
            self.nm.add_notification(user_id, filler_name, metadata["status"])
            quit_chromedriver(driver)
            if lock_file.exists():
                lock_file.unlink()