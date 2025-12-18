# gformfiller/core/filler_worker

import logging
import os
from typing import Dict, Any, Optional

from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager
from gformfiller.infrastructure.driver import get_chromedriver, quit_chromedriver

from gformfiller.domain.form_filler import FormFiller
from gformfiller.domain.ai import create_ai_client

logger = logging.getLogger(__name__)


class FillerWorker:
    def __init__(self, folder_manager: FolderManager, config_manager: ConfigManager):
        self.fm = folder_manager
        self.cm = config_manager

    def is_profile_locked(self, profile_name: str) -> bool:
        lock_file = self.fm.profiles_dir / profile_name / ".lock"
        return lock_file.exists()

    def run(self, filler_name: str, form_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exécute le cycle d'automatisation.
        :param filler_name: Nom du filler cible.
        :param form_data: Données de formulaire optionnelles (écrase le contenu de formdata.json).
        """
        # 1. Résolution de la configuration et des métadonnées
        config = self.cm.get_resolved_config(filler_name)
        metadata = self.fm.get_filler_file_content(filler_name, "metadata")
        
        # Si form_data n'est pas passé en paramètre, on le charge depuis le fichier local
        if form_data is None:
            form_data = self.fm.get_filler_file_content(filler_name, "formdata")

        if not metadata.get("url"):
            logger.error(f"URL absente pour le filler: {filler_name}")
            return False

        # 2. Préparation du Driver
        driver_path = str(self.fm.root / "chromedriver" / "chromedriver")
        binary_loc = str(self.fm.root / "chrome-testing" / "chrome")
        profile_path = str(self.fm.profiles_dir / config.profile)
        lock_file = self.fm.profiles_dir / config.profile / ".lock"

        if self.is_profile_locked(config.profile):
            logger.error(f"Profile {config.profile} is locked. Another instance is running.")
            return False

        driver = get_chromedriver(
            driver_path=driver_path,
            binary_location=binary_loc,
            user_data_dir=profile_path,
            headless=config.headless,
            remote=config.remote,
            no_sandbox=True
        )

        try:
            lock_file.touch()

            # 3. Gestion de l'IA conditionnelle
            ai_client = None
            driver.get(metadata["url"])
            # 4. Initialisation du moteur FormFiller
            filler_engine = FormFiller(
                driver=driver,
                form_data=form_data,
                screenshots_dir=str(self.fm.fillers_dir / filler_name / "record" / "screenshots"),
                output_dir=str(self.fm.fillers_dir / filler_name / "record" / "pdfs"),
                submit=config.submit
            )

            # 5. Exécution
            success = filler_engine.run()
            
            # Mise à jour de l'état
            metadata["status"] = "completed" if success else "failed"
            self.fm.update_filler_file_content(filler_name, "metadata", metadata)
            
            return success

        except Exception as e:
            logger.exception(f"Erreur critique lors de l'exécution de '{filler_name}': {e}")
            metadata["status"] = "error"
            self.fm.update_filler_file_content(filler_name, "metadata", metadata)
            return False
            
        finally:
            quit_chromedriver(driver)
            if lock_file.exists():
                lock_file.unlink()