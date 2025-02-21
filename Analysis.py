import mysql.connector
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import json


class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "Ronak@1234"
        self.database = "face_attendance_system"
        try:
            self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
            )
            self.cursor = self.connection.cursor(buffered=True)
            print("Connected to database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            print(self.connection)

    def Connection(self):
        return self.connection


if __name__ == "__main__" :
    db = Database()
    connection = db.Connection()
    cursor = connection.cursor(buffered=True)
    print("Connected to database")

    query = "select * from attendance_table"
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        attendance_count = defaultdict(int) 
        per_day_emp_attendance = defaultdict(int)   # intime , outtime and number of in and out time per employee
        per_date_emp_attendance = defaultdict(int)   # on each day details of every employee
        for rows in result:
            emp_data = json.loads(rows[3])

            for date , details in emp_data.items():
                if details["InTime"]:
                    attendance_count[date]  = attendance_count[date] + 1
                    if len(details["InTime"]) > 1:
                        intime = details["InTime"][0]
                        NumberOfTime = len(details["InTime"])
                    else:
                        intime = None
                        NumberOfTime = None

                    if len(details["OutTime"]) > 1:
                        outime = details["OutTime"][0]
                    else:
                        outime = None


                    json_temp = {"InTime" : intime , "NumberOfTime" : NumberOfTime , "OutTime" : outime}
                    json_temp = json.dumps(json_temp)
                    per_day_emp_attendance[rows[1]] = json_temp
                else:
                    json_temp = {"InTime" : None , "NumberOfTime" : None , "OutTime" : None}
                    json_temp = json.dumps(json_temp)
                    per_day_emp_attendance[rows[1]] = json_temp
                
                per_date_emp_attendance[date] = per_day_emp_attendance
            
        for date , details in per_date_emp_attendance.items():
            print(f"Attendance on {date} : {details}")
    else:
        print("No Attendance data found in the database")


    cursor.close()
    connection.close()
    print("Connection closed")    
