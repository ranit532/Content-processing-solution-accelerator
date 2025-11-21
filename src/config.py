import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KEYVAULT_NAME = os.getenv("KEYVAULT_NAME")
COSMOS_KEY = os.getenv("COSMOS_KEY")
BLOB_CONN = os.getenv("BLOB_CONN")
QUEUE_CONN = os.getenv("QUEUE_CONN")

# Try to load secrets from Key Vault if not provided via env vars
if KEYVAULT_NAME:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        vault_url = f"https://{KEYVAULT_NAME}.vault.azure.net"
        secret_client = SecretClient(vault_url=vault_url, credential=credential)

        if not OPENAI_API_KEY:
            OPENAI_API_KEY = secret_client.get_secret('OPENAI_API_KEY').value
        if not COSMOS_KEY:
            try:
                COSMOS_KEY = secret_client.get_secret('COSMOS_KEY').value
            except Exception:
                COSMOS_KEY = None
        if not BLOB_CONN:
            try:
                BLOB_CONN = secret_client.get_secret('BLOB_CONN').value
            except Exception:
                BLOB_CONN = None
        if not QUEUE_CONN:
            try:
                QUEUE_CONN = secret_client.get_secret('QUEUE_CONN').value
            except Exception:
                QUEUE_CONN = None
    except Exception:
        # If Key Vault retrieval fails, fall back to env vars
        pass

# Fallback defaults
if not BLOB_CONN:
    BLOB_CONN = os.getenv("BLOB_CONN", "UseDevelopmentStorage=true")
if not QUEUE_CONN:
    QUEUE_CONN = os.getenv("QUEUE_CONN", "UseDevelopmentStorage=true")