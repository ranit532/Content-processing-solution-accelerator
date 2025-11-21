import os
from azure.cosmos import CosmosClient, PartitionKey
from config import COSMOS_KEY

# --- Load Environment Variables ---
DB_URL = os.getenv("COSMOS_URL")
DB_KEY = COSMOS_KEY or os.getenv("COSMOS_KEY")
DB_NAME = os.getenv("COSMOS_DB", "contentdb")
CONTAINER_NAME = "results"

# Partition key from .env (fallback to /doc_id)
PARTITION_KEY_PATH = os.getenv("COSMOS_PARTITION_KEY", "/doc_id")

# --- Cosmos Client ---
client = CosmosClient(DB_URL, credential=DB_KEY)


def get_container():
    """
    Returns the container client without trying to recreate
    the database or container. This avoids invalid input errors.
    """
    db = client.get_database_client(DB_NAME)
    container = db.get_container_client(CONTAINER_NAME)
    return container


def upsert_result(doc: dict):
    """
    Inserts or updates the document.
    The document MUST contain `doc_id` since partition key = /doc_id.
    """
    if "doc_id" not in doc:
        raise ValueError("Document must include `doc_id` field for partition key.")

    container = get_container()
    return container.upsert_item(doc)


def get_result_by_id(doc_id: str):
    """
    Queries documents using the correct field name: doc_id.
    """
    container = get_container()
    query = f"SELECT * FROM c WHERE c.doc_id = '{doc_id}'"

    try:
        results = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return results[0] if results else None
    except Exception:
        return None


def list_results(limit: int = 50):
    """
    Reads all items.
    """
    container = get_container()
    return list(container.read_all_items(max_item_count=limit))


def update_result_validation(doc_id: str, changes: dict):
    """
    Updates validation results on a record.
    """
    record = get_result_by_id(doc_id)
    if not record:
        return False

    record.update({
        "validated": True,
        "validated_changes": changes
    })

    upsert_result(record)
    return True
