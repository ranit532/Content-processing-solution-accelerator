import os
from azure.cosmos import CosmosClient, PartitionKey
from config import COSMOS_KEY

DB_URL = os.getenv("COSMOS_URL")
DB_KEY = COSMOS_KEY or os.getenv("COSMOS_KEY")
DB_NAME = os.getenv("COSMOS_DB", "contentdb")

client = CosmosClient(DB_URL, credential=DB_KEY)

def get_container():
    try:
        db = client.create_database(DB_NAME)
    except Exception:
        db = client.get_database_client(DB_NAME)
    try:
        container = db.create_container(id="results", partition_key=PartitionKey(path="/doc_id"))
    except Exception:
        container = db.get_container_client("results")
    return container


def upsert_result(doc: dict):
    c = get_container()
    c.upsert_item(doc)


def get_result_by_id(doc_id: str):
    c = get_container()
    try:
        res = list(c.query_items(query=f"SELECT * FROM c WHERE c.doc_id = '{doc_id}'", enable_cross_partition_query=True))
        return res[0] if res else None
    except Exception:
        return None


def list_results(limit: int = 50):
    c = get_container()
    return list(c.read_all_items(max_item_count=limit))


def update_result_validation(doc_id: str, changes: dict):
    res = get_result_by_id(doc_id)
    if not res:
        return False
    res.update({"validated": True, "validated_changes": changes})
    upsert_result(res)
    return True
