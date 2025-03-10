import streamlit as st
from PIL import Image
import io
import mysql.connector


if __name__ == "__main__":
    try:
            connection = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password ="Ronak@1234",
                database = "face_attendance_system"
            )
            cursor = connection.cursor(buffered=True)
            st.write("Connected to database")
    except Exception as e:
            st.write(f"An unexpected error occurred: {str(e)}")
        
    try:
            st.title("Unknown Faces In the Database")
            query = "select * from log_table where problem_type = 'Unknown Face'"
            cursor.execute(query)
            result = cursor.fetchall()

            if len(result) > 0:
                for res in result:
                    date = res[1]
                    blob_data = res[3]
                    image = Image.open(io.BytesIO(blob_data))
                    st.title(date)
                    st.image(image , caption="Unknown Face" , use_container_width =True)
                    st.write()
            else:
                st.title("Database has no record of the unknown face right now")
    except Exception as e:
            st.write("Error occur while fetching unknown face data :: " , e)
        
    try:
            st.title("Error Registerd in Database")
            query = "select * from log_table where problem_type = 'Error'"
            cursor.execute(query)
            result = cursor.fetchall()

            if len(result) > 0:
                for res in result:
                    date = res[1]
                    blob_data = res[3]
                    image = Image.open(io.BytesIO(blob_data))
                    st.title(date)
                    st.image(image , caption="Error" , use_container_width =True)
                    st.write()
            else:
                st.title("Database has no record of the ERROR right now")

    except Exception as e:
            st.write("Error occur while fetching unknown face data :: " , e)
        


        
