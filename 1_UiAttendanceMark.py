import streamlit as st

# Set the title of the app
st.set_page_config(page_title="Face Recognition Attendance System", layout="wide")

st.title("Attendance Marking System using Face Recognition")
st.markdown("""
    ## Welcome to the Attendance Marking System

    Our attendance marking system leverages advanced face recognition technology to provide a seamless and efficient way to track employee attendance. This system offers an intuitive interface for capturing images, displaying recognition results, and logging attendance data.

    ### Key Features

    - **Face Recognition**: Utilizes state-of-the-art face recognition algorithms to identify employees accurately.
    - **Real-Time Attendance**: Capture and mark attendance in real-time with instant feedback.
    - **Attendance Logs**: Maintain detailed logs of successful recognitions, failures, and abnormal conditions.
    - **User-Friendly Interface**: Easy-to-use interface for capturing images and viewing results.

    ### How It Works

    1. **Capture Image**: Use the interface to capture an image of the employee.
    2. **Face Recognition**: The system processes the image to recognize the employee's face.
    3. **Attendance Marking**: If the face is recognized, the attendance is marked, and the result is displayed.
    4. **Logging**: All recognition attempts, including failures and abnormal conditions, are logged for future reference.

    ### Getting Started

    - **Navigate to the Attendance Page**: Use the sidebar to navigate to the attendance marking page.
    - **Capture Image**: Click on the "Capture Image" button to start the recognition process.
    - **View Results**: The recognition result and attendance status will be displayed on the screen.
    - **Check Logs**: Access the logs to view the history of recognition attempts and any abnormal conditions.

    ### Benefits

    - **Accurate Attendance Tracking**: Ensures accurate and reliable attendance tracking.
    - **Time-Saving**: Reduces the time and effort required for manual attendance marking.
    - **Enhanced Security**: Provides an additional layer of security by verifying employee identity.

    ### Contact Us

    For any inquiries or support, please contact our support team at [65ronakvekariya@gmail.com](mailto:65ronakvekariya@gmail.com).

    """)


# # Load selected page
# if page == "Home":
#     st.title("Welcome to Face Recognition Attendance System")
#     st.markdown("## Use the sidebar to navigate.")
# elif page == "Mark Attendance":
#     from pages.mark_attendance import mark_attendance
#     mark_attendance()
# elif page == "View Attendance":
#     from pages.view_attendance import view_attendance
#     view_attendance()
