import os


APP_NAME = "MYIA"
APP_ENV = "development"
LOG_LEVEL = "INFO"

CONFLUENCE_ENABLED = os.getenv("CONFLUENCE_ENABLED", "false").lower() == "true"
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

JIRA_ENABLED = os.getenv("JIRA_ENABLED", "false").lower() == "true"
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
