# Face Recognition Attendance System

An end-to-end computer-vision attendance prototype that detects and recognizes faces, stores facial embeddings, marks attendance, and exposes attendance analysis through a web interface.

## System architecture

```
Camera / image
      ↓
Face detection
      ↓
DeepFace / ArcFace embedding
      ↓
Cosine-distance matching
      ↓
Known / Unknown classification
      ↓
Attendance + event database
      ↓
Django / Streamlit analysis
```

## What it demonstrates

- Multi-face detection from camera images.
- Facial embedding generation with DeepFace / ArcFace.
- Identity matching using cosine distance.
- Known and unknown face handling.
- MySQL-backed employee and attendance records.
- Attendance in/out tracking.
- Unknown-face and error logging.
- Web-based attendance analysis.

## Technology

**Python · OpenCV · DeepFace · ArcFace · SciPy · MySQL · Django · Streamlit · Pandas · Plotly**

## Core components

| Component | Role |
| --- | --- |
| `FaceRecognizer.py` | Detects faces, generates embeddings, and matches them against stored embeddings. |
| `AttendanceMark.py` | Handles attendance persistence and database interaction. |
| `DatabaseEmbeddingsInsert.py` | Generates employee embeddings and stores them in the database. |
| `demo.py` | Connects the recognition workflow with attendance marking and logging. |
| `attendance/` | Django application and supporting backend components. |
| `pages/` | Streamlit views for attendance, analysis, and system logs. |

## Configuration

The application expects database configuration through environment variables:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-local-password
DB_NAME=face_attendance_system
DB_PORT=3306
```

Start with `.env.example` and keep your real `.env` file out of version control.

## Data policy for this repository

The original development project used real face images and generated biometric embeddings. Those development artifacts are intentionally **not included in this portfolio repository**.

For a public portfolio version, use synthetic or consented demo data and never commit:

- face image datasets;
- raw biometric embeddings;
- employee contact information;
- attendance databases;
- unknown-person captures.

This repository therefore documents the engineering and application code without publishing the underlying biometric dataset.

## Running locally

A local setup requires your own MySQL database and a local face dataset/embedding store. The code is structured around the original project layout, so database schema and local data preparation are prerequisites.

```bash
python -m venv .venv
pip install -r requirements.txt
```

Configure the database environment variables, prepare your local data, and run the relevant application entry point.

## Engineering considerations

Because this system handles biometric information, a production implementation would additionally require strong access control, encryption, retention/deletion policies, consent and governance controls, threshold calibration, audit logging, and security testing.

Further engineering improvements include:

- separating recognition, persistence, and UI layers;
- replacing ad-hoc database queries with a dedicated repository/service layer;
- adding automated tests and CI;
- benchmarking recognition latency and accuracy;
- making the recognition threshold configurable and evaluated on a validation set;
- containerizing the application for reproducible deployment.

## Portfolio context

This project is one of the strongest examples in my portfolio of connecting an ML component to a larger software system: **computer vision → embedding generation → similarity matching → database persistence → attendance workflow → analytics**.

## Author

**Ronak Vekariya**

[GitHub](https://github.com/Ronakvekariya)
