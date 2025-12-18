# gformfiller/infrastructure/folder_manager/constants.py

from enum import Enum

# Directories
PROFILES_DIR = "profiles"
FILLERS_DIR = "fillers"
CHROME_BIN_DIR = "chrome-testing"
CHROMEDRIVER_DIR = "chromedriver"

# Filler Sub-directories
RECORD_DIR = "record"
PDFS_DIR = "pdfs"
SCREENSHOTS_DIR = "screenshots"
FILES_DIR = "files"

# Standard Files
CONFIG_FILE = "config.json"
METADATA_FILE = "metadata.json"
FORMDATA_FILE = "formdata.json"
FILLER_LOG_FILE = "log"

# Global System Files
GLOBAL_LOG_DB = "log.db"
DEFAULT_TOML = "default.toml"

# Default Conten
DEFAULT_FORMAT_FILE_CONTENT: dict[str, dict[str, str]] = {
    "TextResponse": {},
    "DateResponse": {},
    "TimeResponse": {},
    "CheckboxResponse": {},
    "RadioResponse": {},
    "ListboxResponse": {},
    "FileUploadResponse": {}
}