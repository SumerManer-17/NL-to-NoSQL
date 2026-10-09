
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


SCHEMA_DIR = Path("schema_versions")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "mongodb_schema"

# Local embedding model. Downloads the model on first use.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


client = chromadb.PersistentClient(path=CHROMA_DIR)
model = SentenceTransformer(EMBEDDING_MODEL)


def load_latest_schema():
    schema_files = list(SCHEMA_DIR.glob("students_v*.json"))

    if not schema_files:
        raise FileNotFoundError(
            "No schema snapshots found in schema_versions/"
        )

    def version_number(path):
        return int(path.stem.rsplit("_v", 1)[1])

    latest_file = max(schema_files, key=version_number)

    with latest_file.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    print(f"Loaded schema: {latest_file}")
    return schema


def build_field_documents(schema):
    documents = []
    ids = []
    metadatas = []

    for field in schema["fields"]:
        path = field["path"]
        types = ", ".join(field["types"])
        samples = ", ".join(
            str(value) for value in field.get("sample_values", [])
        )

        document = (
            f"MongoDB collection: {schema['collection']}. "
            f"Field: {path}. "
            f"Data types: {types}. "
            f"Sample values: {samples}."
        )

        documents.append(document)
        ids.append(f"{schema['collection']}:{path}")
        metadatas.append({
            "collection": schema["collection"],
            "field_path": path,
            "types": types,
        })

    return ids, documents, metadatas


def index_schema():
    schema = load_latest_schema()


    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


    ids, documents, metadatas = build_field_documents(schema)

    if not ids:
        print("No fields found in the schema.")
        return

    # Upsert updates existing field documents and inserts new ones.
    embeddings = model.encode(documents).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    # Remove fields that disappeared from the latest snapshot.
    current_ids = set(ids)
    existing = collection.get()

    stale_ids = [
        item_id for item_id in existing["ids"]
        if item_id not in current_ids
    ]

    if stale_ids:
        collection.delete(ids=stale_ids)

    print(f"Indexed {len(ids)} schema fields into ChromaDB.")


def retrieve_schema(query, top_k=5):
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        raise RuntimeError(
            "Schema index is empty. Run index_schema() first."
        )

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    return results


if __name__ == "__main__":
    index_schema()

    test_query = "Find students with high GPA and their academic department"
    results = retrieve_schema(test_query)

    print("\nQuery:", test_query)
    print("\nRetrieved schema fields:")

    for metadata, document, distance in zip(
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0],
    ):
        print(f"- {metadata['field_path']} (distance: {distance:.4f})")
        print(f"  {document}")
