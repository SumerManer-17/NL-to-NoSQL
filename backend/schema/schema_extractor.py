from typing import Any

from backend.database.mongodb import get_database
from backend.schema.schema_models import FieldSchema, CollectionSchema


MAX_SAMPLE_VALUES = 5


def get_mongodb_type(value: Any) -> str:
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "double"

    if isinstance(value, str):
        return "string"

    if isinstance(value, dict):
        return "object"

    if isinstance(value, list):
        return "array"

    return type(value).__name__


def add_field(
    fields: dict[str, dict[str, Any]],
    path: str,
    value: Any
):
    field_type = get_mongodb_type(value)

    if path not in fields:
        fields[path] = {
            "types": set(),
            "sample_values": []
        }

    fields[path]["types"].add(field_type)

    if (
        value is not None
        and not isinstance(value, (dict, list))
        and value not in fields[path]["sample_values"]
        and len(fields[path]["sample_values"]) < MAX_SAMPLE_VALUES
    ):
        fields[path]["sample_values"].append(value)


def extract_fields(
    document: dict[str, Any],
    fields: dict[str, dict[str, Any]],
    prefix: str = ""
):
    for key, value in document.items():

        path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):

            add_field(fields, path, value)

            extract_fields(
                value,
                fields,
                path
            )

        elif isinstance(value, list):

            add_field(fields, path, value)

            for item in value:

                if isinstance(item, dict):
                    extract_fields(
                        item,
                        fields,
                        path
                    )

                elif item is not None:

                    item_path = f"{path}[]"

                    add_field(
                        fields,
                        item_path,
                        item
                    )

        else:

            add_field(
                fields,
                path,
                value
            )


def extract_collection_schema(
    collection_name: str,
    sample_size: int = 100
) -> CollectionSchema:

    db = get_database()

    collection = db[collection_name]

    documents = collection.find().limit(sample_size)

    fields: dict[str, dict[str, Any]] = {}

    for document in documents:

        document.pop("_id", None)

        extract_fields(
            document,
            fields
        )

    schema_fields = []

    for path, data in sorted(fields.items()):

        schema_fields.append(
            FieldSchema(
                path=path,
                types=sorted(data["types"]),
                sample_values=data["sample_values"]
            )
        )

    return CollectionSchema(
        collection=collection_name,
        fields=schema_fields
    )


if __name__ == "__main__":

    schema = extract_collection_schema("students")

    print(
        schema.model_dump_json(
            indent=2
        )
    )