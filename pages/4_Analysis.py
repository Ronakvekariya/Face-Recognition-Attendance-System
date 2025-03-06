import mysql.connector
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import json
from datetime import datetime
import streamlit as st
import plotly.express as px


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

# Function to count employees present per date
def count_employees(data):
    attendance_count = {}
    for date, records in data.items():
        attendance_count[date] = len(records)  # Count number of employees present
    return attendance_count

def AnalysisResult():
    db = Database()
    connection = db.Connection()
    cursor = connection.cursor(buffered=True)
    print("Connected to database")

    query = "select * from attendance_table"
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        attendance_count = defaultdict(int) 
        per_day_emp_attendance = {}  # intime , outtime and number of in and out time per employee
        per_date_emp_attendance = {}  # on each day details of every employee
        for rows in result:
            emp_data = json.loads(rows[3])

            for date , details in emp_data.items():
                if details["InTime"]:
                    attendance_count[date]  = attendance_count[date] + 1
                    if len(details["InTime"]) >= 1:
                        intime = details["InTime"][0]
                        NumberOfTime = len(details["InTime"])
                    else:
                        intime = None
                        NumberOfTime = None

                    if len(details["OutTime"]) >= 1:
                        outime = details["OutTime"][0]
                    else:
                        outime = None


                    json_temp = {"InTime" : intime , "NumberOfTime" : NumberOfTime , "OutTime" : outime}
                    json_temp = json.dumps(json_temp)
                    # per_day_emp_attendance[rows[1]].append(json_temp)
                else:
                    json_temp = {"InTime" : None , "NumberOfTime" : None , "OutTime" : None}
                    json_temp = json.dumps(json_temp)
                
                if str(rows[1]) not in per_day_emp_attendance.keys():
                    per_day_emp_attendance[str(rows[1])] = {}
                    
                per_day_emp_attendance[str(rows[1])][date] = json_temp

                
                
        
            emp_data = json.loads(rows[3])

            for date , details in emp_data.items():
                if details["InTime"]:
                        if len(details["InTime"]) >= 1:
                                intime = details["InTime"][0]
                                
                                NumberOfTime = len(details["InTime"])
                        else:
                                intime = None
                                NumberOfTime = None

                        if len(details["OutTime"]) >= 1:
                                outime = details["OutTime"][0]
                        else:
                                outime = None 
                        temp = {"InTime" : intime , "NumberOfTime" : NumberOfTime , "OutTime" : outime}
                        temp = json.dumps(temp) 

                        if date not in per_date_emp_attendance:
                            per_date_emp_attendance[date] = {}

                        per_date_emp_attendance[date][rows[1]] = temp
    
    cursor.close()
    connection.close()
    print("Connection closed")

    return [attendance_count , per_day_emp_attendance , per_date_emp_attendance]            


if __name__ == "__main__" :

    attendance_count , per_day_emp_attendance , per_date_emp_attendance = AnalysisResult()
    for date , count in attendance_count.items():
        print("Number of Employee came on " , date , " is " , count)

    print("\n\n\n\n\n")

    print("Now details of each employee on each day")

    for key in per_day_emp_attendance.items():
            print(key)
        
    print("\n\n\n\n")
            

    temp = dict(sorted(per_date_emp_attendance.items(), key=lambda x: datetime.strftime(x[0], "%Y-%m-%d")))

            
    for date , details in temp.items():
        print(date)
        for empId , json_Data in details.items():
                print("EmployeeId " , empId , " Details " , json_Data)

    attendance_data = count_employees(per_date_emp_attendance)
    df = pd.DataFrame(list(attendance_data.items()), columns=["Date", "Employees Present"])
    df["Date"] = pd.to_datetime(df["Date"])  # Convert Date to DateTime format
    df = df.sort_values("Date")  # Sort DataFrame by Date

    # Streamlit UI
    st.title("Employee Attendance Analysis")
    st.write("This dashboard displays the number of employees present on each date.")

    # Table Display
    st.subheader("Attendance Data")
    st.dataframe(df)

    # Matplotlib Plot
    st.subheader("Attendance Trend Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["Employees Present"], marker='o', linestyle='-', color='b', label="Employees Present")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Employees")
    ax.set_title("Employee Attendance Trend")
    ax.grid()
    ax.legend()
    st.pyplot(fig)

    # Interactive Plotly Chart
    st.subheader("Interactive Attendance Graph")
    fig2 = px.bar(df, x="Date", y="Employees Present", title="Employees Present Per Date", labels={"Date": "Date", "Employees Present": "Number of Employees"})
    st.plotly_chart(fig2)



    


