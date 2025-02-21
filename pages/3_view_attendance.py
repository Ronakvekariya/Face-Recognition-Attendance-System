import streamlit as st
from PIL import Image
import mysql.connector
import json
import pandas as pd


# Add custom CSS for styling
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        height: 3em;
        width: 15em;
        border-radius: 10px;
        border: 2px #4CAF50 solid;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: white;
        color: #4CAF50;
        border: 2px #4CAF50 solid;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title of the app
st.title("View Attendance")




# Function to display attendance
def view_attendance():
    EmployeeId = st.session_state.employee_id
    if EmployeeId is not None:
            try:
                for emp_id in EmployeeId:
                    query = f"SELECT * FROM attendance_table WHERE employee_id = {emp_id[1]}"
                    cursor.execute(query)
                    result = cursor.fetchall()

                    if result:
                        st.write(f"### Attendance Sheet of the Employee: {emp_id[0]}")

                        json_data = result[0][3]
                        json_data = json.loads(json_data)

                        rows = []
                        for date, times in json_data.items():
                            in_times = times['InTime']
                            out_times = times['OutTime']
                            max_length = max(len(in_times), len(out_times))

                            # Ensure both lists have the same length by padding with 'N/A'
                            in_times += ['N/A'] * (max_length - len(in_times))
                            out_times += ['N/A'] * (max_length - len(out_times))

                            # Add rows with the date only for the first entry
                            for i, (in_time, out_time) in enumerate(zip(in_times, out_times)):
                                rows.append({'Date': date if i == 0 else '', 'InTime': in_time, 'OutTime': out_time})

                        # Create a DataFrame from the processed data
                        attendance_df = pd.DataFrame(rows)
                        st.dataframe(attendance_df)
            except Exception as e:
                st.write("Please first perorm face recognition or no face is detected")
    else:
        st.write(f"No attendance data found for Employee ID: {emp_id[1]}")

if __name__ == "__main__":
    if "connection" not in st.session_state:
        st.title("Mark your attendance first")
    elif "connection" in st.session_state:
        try:
            connection = st.session_state.connection
            cursor = connection.cursor(buffered=True)
            st.write("Connected to database")
        except mysql.connector.Error as err:
            st.error(f"Database connection error: {err}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
        view_attendance()