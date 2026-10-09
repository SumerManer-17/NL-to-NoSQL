
import json
from pathlib import Path


def load_schema(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def compare_schemas(old_schema: dict, new_schema: dict) -> dict:
    old_fields = {
        field["path"]: set(field["types"])
        for field in old_schema["fields"]
    }

    new_fields = {
        field["path"]: set(field["types"])
        for field in new_schema["fields"]
    }

    old_paths = set(old_fields)
    new_paths = set(new_fields)

    added_fields = sorted(new_paths - old_paths)
    removed_fields = sorted(old_paths - new_paths)

    changed_types = {}

    for path in sorted(old_paths & new_paths):
        if old_fields[path] != new_fields[path]:
            changed_types[path] = {
                "old": sorted(old_fields[path]),
                "new": sorted(new_fields[path])
            }

    return {
        "collection": new_schema["collection"],
        "added_fields": added_fields,
        "removed_fields": removed_fields,
        "changed_types": changed_types
    }


if __name__ == "__main__":
    old_path = Path("schema_versions/students_v1.json")
    new_path = Path("schema_versions/students_v2.json")

    if not old_path.exists() or not new_path.exists():
        print("Create both students_v1.json and students_v2.json first.")
    else:
        old_schema = load_schema(str(old_path))
        new_schema = load_schema(str(new_path))

        changes = compare_schemas(old_schema, new_schema)
        print(json.dumps(changes, indent=4))
