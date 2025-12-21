# gformfiller/infrastructure/folder_manager/constants.py

ROOT_DIR = "gformfiller"

# Directories
PROFILES_DIR = "profiles"
CHROME_BIN_DIR = "chrome-testing"
CHROMEDRIVER_DIR = "chromedriver"
USERS_DIR = "users"

# User Sub-directories
FILLERS_SUBDIR = "fillers"

# Filler Sub-directories
RECORD_SUBDIR = "record"
PDFS_SUBDIR = "pdfs"
SCREENSHOTS_SUBDIR = "screenshots"
FILES_SUBDIR = "files"

# Per-Filler Files
CONFIG_FILE = "config.json"
METADATA_FILE = "metadata.json"
FORMDATA_FILE = "formdata.json"
FILLER_LOG_FILE = "log.txt"

# Per-User Files
NOTIFICATIONS_DB = "notifications.db"
LOG_DB = "log.db"

# Global System Files
GLOBAL_LOG_DB = "log.db"
USERS_DB = "users.db"
DEFAULT_CONFIG = "default.toml"

# Default Content
DEFAULT_FORMAT_FILE_CONTENT: dict[str, dict[str, str]] = {
    "TextResponse": {},
    "DateResponse": {},
    "TimeResponse": {},
    "CheckboxResponse": {},
    "RadioResponse": {},
    "ListboxResponse": {},
    "FileUploadResponse": {}
}

# Lock file

LOCK_FILE = ".gformprofile_lock"

class FileKeys:
    METADATA = "metadata"
    FORMDATA = "formdata"
    CONFIG = "config"