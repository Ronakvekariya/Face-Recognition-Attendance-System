import json
import os
from datetime import datetime

import cv2
import mysql.connector
from scipy.spatial.distance import cosine

from FaceRecognizer import Recongnizer


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


class AttendanceMark:
    def __init__(self):
        config = get_db_config()
        self.host = config["host"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config["database"]
        self.image_path = "./test.jpg"
        print("Initializing AttendanceMark")
        try:
            self.connection = mysql.connector.connect(**config)
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

    def UnknownFace(self, embeddings=None, min_distance=0.5):
        Count = 0
        query = "select * from log_table where problem_type = 'Unknown Face'"
        self.cursor = self.connection.cursor(buffered=True)
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        if len(result) != 0:
            for res in result:
                if res[5] == '{}':
                    continue
                else:
                    temp = json.loads(res[5])
                    distance = cosine(embeddings, temp['embedding'])
                    if distance < min_distance:
                        min_distance = distance
                        Count += 1

            return [True, Count]
        else:
            return [False, 0]

    def MarkAttendance(self):
        EmployeeId = []
        count = 0
        print("Running demo method")
        rec = Recongnizer()
        faces = rec.InAction()
        if isinstance(faces, str):
            print(faces)
            print("Error in processing face")
            with open(self.image_path, 'rb') as file:
                binary_data = file.read()
            query = "select * from log_table"
            self.cursor.execute(query)
            NumOfRows = self.cursor.rowcount
            query = "insert into log_table (id , timestamp, problem_type , image , detail, face_embedding) values (%s, %s, %s, %s, %s , %s)"
            self.cursor.execute(query, (NumOfRows + 1, datetime.now(), "Error", binary_data, faces, '{}'))
            self.connection.commit()
        else:
            for face in faces:
                count = count + 1
                if type(face) != str and face[0] != "Unknown":
                    EmployeeId.append([face[0], face[3], face[4], None])
                    query = f"SELECT * FROM employee WHERE id = {face[3]}"
                    self.cursor.execute(query)
                    result = self.cursor.fetchall()
                    employee_id = result[0][0]
                    print(employee_id)
                    query = "select * from attendance_table where employee_id = %s"
                    self.cursor.execute(query, (employee_id,))
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
                            print(len(attendace_json[current_date]["InTime"]), "   ", len(attendace_json[current_date]["OutTime"]))
                            if len(attendace_json[current_date]["InTime"]) == len(attendace_json[current_date]["OutTime"]):
                                attendace_json[current_date]["InTime"].append(current_time)
                                query = "UPDATE attendance_table SET attendance = %s WHERE employee_id = %s"
                                json_data = json.dumps(attendace_json)
                                self.cursor.execute(query, (json_data, employee_id))
                                self.connection.commit()
                            else:
                                attendace_json[current_date]["OutTime"].append(current_time)
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
                        self.cursor.execute(query, (NumOfRowsTemp, employee_id, CurrentTimestamp, json_data))
                        self.connection.commit()
                        print("Attendance Marked")
                    else:
                        print("Error")
                else:
                    if face[0] == "Unknown":
                        print("Unknown face detected")
                        image = cv2.imread(self.image_path)
                        x, y, w, h = face[2]['x'], face[2]['y'], face[2]['w'], face[2]['h']
                        left, top, right, bottom = x, y, x + w, y + h
                        height, width = image.shape[:2]
                        print(f"Left: {left}, Top: {top}, Right: {right}, Bottom: {bottom}")
                        cropped_image = image[top:bottom, left:right]
                        unknown_face_image_path = "./Unknow_face.jpg"
                        try:
                            cv2.imwrite(unknown_face_image_path, cropped_image)
                        except Exception as e:
                            print(f"Error in saving the unknown person image : {e}")
                        with open(unknown_face_image_path, 'rb') as file:
                            binary_data = file.read()
                        query = "select * from log_table"
                        self.cursor.execute(query)
                        NumOfRows = self.cursor.rowcount
                        temp = face[4][0]["embedding"]
                        json_temp = {"embedding": temp}
                        temp = json.dumps(json_temp)
                        query = "insert into log_table (id , timestamp, problem_type , image , detail , face_embedding) values (%s, %s, %s, %s, %s , %s)"
                        self.cursor.execute(query, (NumOfRows + 1, datetime.now(), "Unknown Face", binary_data, "An unknown face was detected , Please check the person", temp))
                        self.connection.commit()
                        EmployeeId.append([face[0], face[3], face[4], cropped_image])
                    elif type(face) == str:
                        print("Error in processing face")
                        with open(self.image_path, 'rb') as file:
                            binary_data = file.read()
                        query = "select * from log_table"
                        self.cursor.execute(query)
                        NumOfRows = self.cursor.rowcount
                        query = "insert into log_table (id , timestamp, problem_type , image , detail, face_embedding) values (%s, %s, %s, %s, %s)"
                        self.cursor.execute(query, (NumOfRows + 1, datetime.now(), "Error", binary_data, face, '{}'))
                        self.connection.commit()

        date = datetime.now().strftime('%Y-%m-%d')
        query = "SELECT count_employee , date FROM current_employee_counter"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        count = 0

        if result:
            count = result[0]
            db_date = result[1].strftime('%Y-%m-%d')
            print(f"Database Date: {db_date}")
            print(f"Current Date: {date}")

            if db_date == date:
                query = "UPDATE current_employee_counter SET count_employee = count_employee + 1 WHERE id = 1;"
                self.cursor.execute(query)
                self.connection.commit()
                count = result[0] + 1
            else:
                query = "UPDATE current_employee_counter SET count_employee = %s, date = %s WHERE id = %s"
                values = (1, date, 1)
                self.cursor.execute(query, values)
                self.connection.commit()
                count = 1
        else:
            print("No records found in the database.")

        self.cursor.close()
        return [EmployeeId, self.connection, count]


if __name__ == "__main__":
    system = AttendanceMark()
    system.UnknownFace()
