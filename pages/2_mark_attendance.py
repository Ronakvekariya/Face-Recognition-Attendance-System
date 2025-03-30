import streamlit as st
from PIL import Image
from AttendanceMark import AttendanceMark

if "employee_id" not in st.session_state:
    st.session_state.employee_id = None
if "connection" not in st.session_state:
    st.session_state.connection = None
if "system" not in st.session_state:
    st.session_state.system = None
if "Count_Employee" not in st.session_state:
    st.session_state.count_employee = 0

system = None

def mark_attendance():
    st.title("Mark Attendance")
    
    if st.button("Capture Image"):
        system = AttendanceMark()
        st.session_state.system = system
        st.write("Recognizing...")
        RetVal = system.MarkAttendance()
        st.session_state.employee_id = RetVal[0]
        st.session_state.connection = RetVal[1]
        st.session_state.count_employee = RetVal[2]
        # st.success(f"Attendance marked for Employee ID: {RetVal[0]}")
        st.title("Result")

def CountingUnknownFace(embeddings):
    system = AttendanceMark()
    answer = system.UnknownFace(embeddings=embeddings)
    if answer[0] == True:
        return answer[1]
    else:
        return 0

if __name__ == "__main__":
    mark_attendance()
    if st.session_state.employee_id is not None:        
        st.write("Attendance marked for the following employees")
        st.write("Current count of On-Premise Employees are : " , st.session_state.count_employee)
        EmployeeId = st.session_state.employee_id
        for emp_id in EmployeeId:
            if emp_id[0] == "Unknown":
                st.write(f"Unknown face detected")
            else:
                st.write(f"Employee Name: {emp_id[0]}      Employee ID: {emp_id[1]}")
        
        image = Image.open("result.jpg")
        st.image(image, caption="RESULT", use_container_width =True)

        for emp_id in EmployeeId:
            if emp_id[0] == "Unknown":
                st.write(f"Unknown face detected")
                Count = st.session_state.system.UnknownFace(embeddings = emp_id[2][0]["embedding"])

                if Count[1] > 0:
                    message =  f"The Unknown face has seen for {Count[1]} times in Tech Elecon" 
                else:
                    message =  "The Unknown face has not seen in Tech Elecon , It is the First time visiting"
                
                # image = Image.open(emp_id[3])
                image = Image.fromarray(emp_id[3])
                st.image(image, caption=message, use_container_width =True)
