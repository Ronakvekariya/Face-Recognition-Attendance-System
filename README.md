# Face Recognition Attendance System

An end-to-end computer-vision attendance prototype using face detection, facial embeddings, database-backed identity matching, and attendance analytics.

## Pipeline

```
Camera image
    ↓
Face detection
    ↓
Face embedding generation
    ↓
Embedding comparison
    ↓
Identity / Unknown classification
    ↓
Attendance database
    ↓
Analysis and system logs
```

## Main capabilities

- Detect multiple faces from camera images.
- Generate facial embeddings with DeepFace / ArcFace.
- Compare embeddings using cosine distance.
- Identify known and unknown faces.
- Record attendance events in MySQL.
- Store attendance history for analysis.
- Provide Streamlit-based analysis and system-log views.

## Technology

**Python · OpenCV · DeepFace · ArcFace · SciPy · MySQL · Django · Streamlit · Pandas · Plotly**

## Repository structure

| Component | Purpose |
| --- | --- |
| `FaceRecognizer.py` | Face detection, embedding generation, and identity matching. |
| `AttendanceMark.py` | Database-backed attendance processing. |
| `DatabaseEmbeddingsInsert.py` | Generates embeddings and stores employee records. |
| `demo.py` | End-to-end attendance flow. |
| `attendance/` | Django application and analysis components. |
| `pages/` | Streamlit analysis / system-log interfaces. |

## Configuration

Database credentials are loaded through environment variables defined in `.env.example`.

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-local-password
DB_NAME=face_attendance_system
DB_PORT=3306
```

Never commit a real `.env` file.

## Security and privacy

This repository is a portfolio representation of a facial-recognition system. Facial images, embeddings, employee records, and attendance information can be sensitive.

Before sharing a production or real-world dataset publicly, replace it with synthetic/demo data and remove real biometric records and identifiers from the repository.

Credentials that were previously committed should be considered compromised even after rotation; rotating them prevents continued use of the old credential but does not erase historical commits.

## Engineering improvements

The current prototype could be strengthened with:

- encrypted / access-controlled biometric storage;
- explicit consent and retention policies;
- threshold calibration and recognition benchmarks;
- unit and integration tests;
- stronger database transaction handling;
- structured logging and monitoring;
- containerized deployment;
- separation of inference, persistence, and UI layers.

## Author

**Ronak Vekariya**

[GitHub](https://github.com/Ronakvekariya)
