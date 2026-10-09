import io
import os

import mysql.connector
import streamlit as st
from PIL import Image


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


if __name__ == "__main__":
    try:
        connection = mysql.connector.connect(**get_db_config())
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
                st.image(image, caption="Unknown Face", use_container_width=True)
                st.write()
        else:
            st.title("Database has no record of the unknown face right now")
    except Exception as e:
        st.write("Error occur while fetching unknown face data :: ", e)

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
                st.image(image, caption="Error", use_container_width=True)
                st.write()
        else:
            st.title("Database has no record of the ERROR right now")

    except Exception as e:
        st.write("Error occur while fetching unknown face data :: ", e)
