from celery import shared_task
from bson import ObjectId

from .rag_core import get_mongo_collection, ingest_text


@shared_task
def ingest_document_task(doc_id: str):
    coll = get_mongo_collection()
    doc = coll.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        return

    text = doc.get("text", "")
    ingest_text(doc_id=str(doc["_id"]), text=text)

    coll.update_one(
        {"_id": doc["_id"]},
        {"$set": {"status": "indexed"}},
    )
