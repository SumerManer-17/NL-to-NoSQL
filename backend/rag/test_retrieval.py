
from backend.rag.schema_retriever import retrieve_schema


TEST_QUERIES = [
    "Find students from Pune",
    "Show students with GPA above 8",
    "Find students who know Python",
    "Show students with their academic department",
    "Find students with email addresses",
    "Find students with phone numbers",
]


if __name__ == "__main__":
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")

        results = retrieve_schema(query, top_k=5)

        fields = [
            metadata["field_path"]
            for metadata in results["metadatas"][0]
        ]

        print("Retrieved fields:", fields)
