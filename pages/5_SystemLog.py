from datetime import datetime
import os

import mysql.connector


def get_db_config():
    missing = [
        name for name in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and configure the values."
        )

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }


date = datetime.now().strftime('%Y-%m-%d')

test_config = get_db_config()
print("Initializing AttendanceMark")

try:
    connection = mysql.connector.connect(**test_config)
    cursor = connection.cursor(buffered=True)
    print("Connected to database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    raise SystemExit(1)
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    raise SystemExit(1)

query = "SELECT count_employee ,  date FROM current_employee_counter"
cursor.execute(query)
result = cursor.fetchone()

if result:
    print(result[1])
else:
    print("No records found in the database.")

cursor.close()
connection.close()
