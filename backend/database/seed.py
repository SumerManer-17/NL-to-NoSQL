from backend.database.mongodb import get_database


students = [
    {
        "student_id": 101,
        "name": "Rahul",
        "department": "CSE",
        "gpa": 8.5,
        "year": 3,
        "city": "Pune"
    },
    {
        "student_id": 102,
        "name": "Priya",
        "department": "ECE",
        "gpa": 7.8,
        "year": 2,
        "city": "Mumbai"
    },
    {
        "student_id": 103,
        "name": "Amit",
        "department": "CSE",
        "gpa": 9.1,
        "year": 4,
        "city": "Kolhapur"
    },
    {
        "student_id": 104,
        "name": "Sneha",
        "department": "Mechanical",
        "gpa": 8.2,
        "year": 3,
        "city": "Nashik"
    },
    {
        "student_id": 105,
        "name": "Neha",
        "department": "CSE",
        "gpa": 7.5,
        "year": 2,
        "city": "Pune"
    }
]


def seed_students():
    db = get_database()

    collection = db["students"]

    collection.delete_many({})

    result = collection.insert_many(students)

    print(f"Inserted {len(result.inserted_ids)} students.")


if __name__ == "__main__":
    seed_students()