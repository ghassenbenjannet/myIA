import os


APP_NAME = "MYIA"
APP_ENV = "development"
LOG_LEVEL = "INFO"

CONFLUENCE_ENABLED = os.getenv("CONFLUENCE_ENABLED", "false").lower() == "true"
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
