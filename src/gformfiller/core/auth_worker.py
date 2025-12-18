# gformfiller/core/auth_worker

import logging
import os
from typing import Dict, Any, Optional

from gformfiller.infrastructure.folder_manager import FolderManager
from gformfiller.infrastructure.config_manager import ConfigManager
from gformfiller.infrastructure.driver import get_chromedriver, quit_chromedriver

from gformfiller.domain.form_filler import FormFiller
from gformfiller.infrastructure.auth import GoogleAuth


logger = logging.getLogger(__name__)

class AuthWorker:
    def __init__(self, folder_manager: FolderManager, config_manager: ConfigManager):
        self.fm = folder_manager
        self.cm = config_manager

    def run(self, profile_name: str) -> bool:
        self.fm.create_profile(profile_name)

        driver_path = str(self.fm.root / "chromedriver" / "chromedriver")
        binary_loc = str(self.fm.root / "chrome-testing" / "chrome")
        profile_path = str(self.fm.profiles_dir / profile_name)

        driver = get_chromedriver(
            driver_path=driver_path,
            binary_location=binary_loc,
            user_data_dir=profile_path,
            no_sandbox=True
        )

        try:
            GoogleAuth(driver).sign_in()
            return True

        except Exception as e:
            logger.exception(f"Erreur critique lors de l'authentification: {e}.")
            return False

        finally:
            quit_chromedriver(driver)