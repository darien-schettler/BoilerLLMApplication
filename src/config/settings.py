import os, sys
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file
load_dotenv(find_dotenv())

# General Configurations
MODEL_NAME = os.getenv("MODEL_NAME", "llama7b")

#########################
# I think I can replace the below with RH config/auth as it takes care of all of this
#########################
# Cloud Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_SERVICE_ACCOUNT_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE")

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

PAPERSPACE_API_KEY = os.getenv("PAPERSPACE_API_KEY")

# Setting up the infrastructure
INFRASTRUCTURE = os.getenv("INFRASTRUCTURE", "paperspace") # Default to paperspace

# Mapping infrastructure to required keys
INFRASTRUCTURE_KEYS = {
    "aws": {
        "access_key_id": AWS_ACCESS_KEY_ID,
        "secret_access_key": AWS_SECRET_ACCESS_KEY,
    },
    "gcp": {
        "project_id": GCP_PROJECT_ID,
        "service_account_file": GCP_SERVICE_ACCOUNT_FILE,
    },
    "azure": {
        "tenant_id": AZURE_TENANT_ID,
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
    },
    "paperspace": {
        "api_key": PAPERSPACE_API_KEY,
    }
}
#########################
