import mysql.connector
from FaceRecognizer import Recongnizer
import json
from datetime import datetime

class AttendanceMark:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "Ronak@1234"
        self.database = "face_attendance_system"
        self.image_path = "./test.jpg"
        print("Initializing AttendanceMark")
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
    
    def CurrentDate(self):
        time = datetime.now()
        current_date = time.strftime("%Y-%m-%d")
        current_time = time.strftime("%H:%M:%S")
        return current_date, current_time

    def MarkAttendance(self):
        print("Running demo method")
        rec = Recongnizer()
        faces = rec.InAction()
        for face in faces:
            if type(face)!= str and face[0] != "Unknown":
                query = f"SELECT * FROM employee WHERE id = {face[3]}"
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                employee_id = result[0][0]
                print(employee_id)
                query = "select * from attendance_table where employee_id = %s"
                self.cursor.execute(query , (employee_id,))
                NumOfRows = self.cursor.rowcount
                result = self.cursor.fetchone()

                print(result)

                if NumOfRows > 0:
                    attendace_json = json.loads(result[3])
                    current_date, current_time = self.CurrentDate()
                    if attendace_json.get(current_date) == None:
                        attendace_json[current_date] = {
                            "InTime": [current_time],
                            "OutTime": []
                        }
                        query = "UPDATE attendance_table SET attendance = %s WHERE employee_id = %s"
                        json_data = json.dumps(attendace_json)
                        self.cursor.execute(query, (json_data, employee_id))
                        self.connection.commit()
                    else:
                        print(len(attendace_json[current_date]["InTime"]) , "   " , len(attendace_json[current_date]["OutTime"]))
                        if len(attendace_json[current_date]["InTime"]) == len(attendace_json[current_date]["OutTime"]):
                            attendace_json[current_date]["InTime"].append(current_time)
                            # json_data = {
                            #     current_date: {
                            #         "InTime": attendace_json[current_date]["InTime"] + [current_time],
                            #         "OutTime": attendace_json[current_date]["OutTime"]
                            #     }
                            #     }   
                            query = "UPDATE attendance_table SET attendance = %s WHERE employee_id = %s"
                            json_data = json.dumps(attendace_json)
                            self.cursor.execute(query, (json_data, employee_id))
                            self.connection.commit()
                        else:
                            attendace_json[current_date]["OutTime"].append(current_time)
                            # json_data = {
                            #     current_date: {
                            #         "InTime": attendace_json[current_date]["InTime"],
                            #         "OutTime": attendace_json[current_date]["OutTime"] + [current_time]
                            #     }
                            # }
                            query = "UPDATE attendance_table SET attendance = %s WHERE employee_id = %s"
                            json_data = json.dumps(attendace_json)
                            self.cursor.execute(query, (json_data, employee_id))
                            self.connection.commit()
                elif NumOfRows == 0:
                    current_date, current_time = self.CurrentDate()
                    json_data = {
                        current_date: {
                            "InTime": [current_time],
                            "OutTime": []
                        }
                    }
                    json_data = json.dumps(json_data)
                    query = "select * from attendance_table"
                    self.cursor.execute(query)
                    NumOfRowsTemp = self.cursor.rowcount
                    NumOfRowsTemp += 1
                    CurrentTimestamp = datetime.now()
                    query = """INSERT INTO attendance_table (id, employee_id, timestamp, attendance)VALUES (%s, %s, %s, %s)"""
                    self.cursor.execute(query , (NumOfRowsTemp, employee_id, CurrentTimestamp, json_data))
                    self.connection.commit()
                    print("Attendance Marked")
                else:
                    print("Error")  
            else :
                if face[0] == "Unknown":
                    print("Unknown face detected")
                            # Read the image in binary mode
                    with open(self.image_path, 'rb') as file:
                        binary_data = file.read()
                    query = "select * from log_table"
                    self.cursor.execute(query)
                    NumOfRows = self.cursor.rowcount
                    query = "insert into log_table (id , timestamp, problem_type , image , detail) values (%s, %s, %s, %s, %s)"
                    self.cursor.execute(query, (NumOfRows + 1, datetime.now(), "Unknown Face", binary_data, "An unknown face was detected , Please check the person"))
                    self.connection.commit()
                elif type(face) == str:
                    print("Error in processing face")
                    with open(self.image_path, 'rb') as file:
                        binary_data = file.read()
                    query = "select * from log_table"
                    self.cursor.execute(query)
                    NumOfRows = self.cursor.rowcount
                    query = "insert into log_table (id , timestamp, problem_type , image , detail) values (%s, %s, %s, %s, %s)"
                    self.cursor.execute(query, (NumOfRows + 1, datetime.now(), "Error", binary_data, face))
                    self.connection.commit()

        self.cursor.close()

                    



if __name__ == "__main__":
    system = AttendanceMark()
    system.MarkAttendance()


