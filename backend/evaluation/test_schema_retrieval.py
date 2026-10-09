
from backend.rag.schema_retriever import retrieve_schema


TEST_CASES = [
    {
        "query": "Find students from Pune",
        "expected_fields": {"city"},
    },
    {
        "query": "Show students with GPA above 8",
        "expected_fields": {"gpa", "academic.gpa"},
    },
    {
        "query": "Find students who know Python",
        "expected_fields": {"skills[]"},
    },
    {
        "query": "Show students with their academic department",
        "expected_fields": {"academic.department"},
    },
    {
        "query": "Find students with email addresses",
        "expected_fields": {"email"},
    },
    {
        "query": "Find students with phone numbers",
        "expected_fields": {"phone"},
    },
]


def evaluate_recall_at_k(test_cases, k=5):
    total_recall = 0.0

    for test_case in test_cases:
        results = retrieve_schema(test_case["query"], top_k=k)

        retrieved_fields = {
            item["field_path"]
            for item in results["metadatas"][0]
        }

        expected = test_case["expected_fields"]
        hits = expected & retrieved_fields
        recall = len(hits) / len(expected)
        total_recall += recall

        print(f"\nQuery: {test_case['query']}")
        print(f"Expected: {sorted(expected)}")
        print(f"Retrieved: {sorted(retrieved_fields)}")
        print(f"Recall@{k}: {recall:.2f}")

    average_recall = total_recall / len(test_cases)
    print(f"\nAverage Recall@{k}: {average_recall:.2%}")


if __name__ == "__main__":
    evaluate_recall_at_k(TEST_CASES, k=5)
