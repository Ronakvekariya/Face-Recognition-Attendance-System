from datetime import datetime
import mysql.connector

# Get current date in 'YYYY-MM-DD' format
date = datetime.now().strftime('%Y-%m-%d')

# Database credentials
host = "localhost"
user = "root"
password = "Ronak@1234"
database = "face_attendance_system"

print("Initializing AttendanceMark")

try:
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor(buffered=True)
    print("Connected to database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()  # Exit if connection fails
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    exit()

# Query to get date from the database
query = "SELECT count_employee ,  date FROM current_employee_counter"
cursor.execute(query)
result = cursor.fetchone()

if result:
    print(result[1])
    # db_date = result[0].strftime('%Y-%m-%d')  # Convert database date to string
    # print(f"Database Date: {db_date}")
    # print(f"Current Date: {date}")

    # if db_date == date:
    #     print("Same date ✅")
    # else:
    #     print("Different date ❌")
else:
    print("No records found in the database.")

# Close connection
cursor.close()
connection.close()
