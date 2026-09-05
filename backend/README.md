# 🚀 Tejaswini Portfolio - Backend Architecture
**Dual-Service Distributed Architecture: Python Flask Gateway & FastAPI AI Compute Engine**

---

## 🏛️ System Architecture Overview

```
[ Frontend Client (Browser / Portfolio UI) ]
                     |
            (HTTP REST / JSON)
                     v
+-------------------------------------------------------------+
|  🌐 FLASK API GATEWAY & ORCHESTRATOR (Port 5000)            |
|  - SQLite Database Persistence (SQLAlchemy)                 |
|  - Schema Validation & Security                             |
|  - Contact Inquiries & Telemetry Logging                   |
|  - Resilient HTTP Client (httpx with Retry & Fallbacks)    |
+-------------------------------------------------------------+
                     |
        (High-Speed Inter-Service HTTP)
                     v
+-------------------------------------------------------------+
|  ⚡ FASTAPI AI & ALGORITHMIC COMPUTE ENGINE (Port 8000)     |
|  - NLP Email Spam Detection & Keyword Extraction            |
|  - Face Biometrics & Anti-Spoof Attendance Engine           |
|  - Procedural Cryptographic CAPTCHA Generator (SVG)         |
|  - Clinical Disease Predictor (Diabetes & Heart Disease)    |
|  - Portfolio Knowledge Base & AI Assistant QA Bot           |
|  - Interactive Swagger OpenAPI Docs (/docs)                 |
+-------------------------------------------------------------+
```

---

## 📂 Project Structure

```
backend/
├── common/
│   ├── config.py              # Centralized environment configs, ports, secrets
│   ├── logger.py              # Structured logging system
│   └── models_schema.py       # Pydantic schemas for data validation
│
├── fastapi_engine/            # FastAPI Microservice (Port 8000)
│   ├── main.py                # FastAPI entry point & CORS
│   ├── routes/
│   │   ├── spam_detector.py   # NLP Spam classifier routes
│   │   ├── face_biometrics.py # Biometric face verification routes
│   │   ├── captcha_security.py# Dynamic SVG CAPTCHA generator
│   │   ├── disease_prediction.py # Clinical health predictor
│   │   └── ai_assistant.py    # Portfolio AI QA Assistant
│   └── services/
│       ├── ml_models.py       # Trained Scikit-Learn TF-IDF & Classifiers
│       └── vision_engine.py   # Biometric embeddings & Anti-spoof engine
│
├── flask_gateway/             # Flask Gateway (Port 5000)
│   ├── app.py                 # Flask App Factory & Blueprint routes
│   ├── database.py            # SQLite Database Models (Contact, Attendance, Logs)
│   ├── client_fastapi.py      # Resilient HTTP Client to FastAPI
│   └── routes/
│       ├── health.py          # Unified system health monitoring
│       ├── api_portfolio.py   # Gateway proxy for AI endpoints
│       ├── api_contact.py     # Contact form persistence & query
│       ├── api_attendance.py  # Attendance storage & verification
│       └── api_analytics.py   # Telemetry & stats
│
├── run_services.py            # Master script to run both servers concurrently
├── requirements.txt           # Python package dependencies
└── tests/
    ├── test_fastapi_engine.py # FastAPI automated test suite
    └── test_flask_gateway.py  # Flask Gateway automated test suite
```

---

## ⚡ Quick Start Instructions

### 1. Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### 2. Run Both Services Concurrently
```powershell
python backend/run_services.py
```
- **Portfolio Frontend**: http://127.0.0.1:5000
- **IT Admin Control Center**: http://127.0.0.1:5000/admin (Default Login: `admin` / `TejaswiniAdmin2026!`)
- **FastAPI AI Engine & Swagger UI**: http://127.0.0.1:8000/docs

### 3. Run Automated Tests
```powershell
python -m unittest discover -s backend/tests -p "test_*.py"
```

---

## 🔐 IT Admin Control Center (`/admin`)

The IT Admin Portal provides full CRUD management:
- **Projects Management**: Add new projects, edit case studies, reorder display sequences, and toggle featured visibility.
- **Skills & Tech Matrix**: Add, update proficiency %, and categorize skills.
- **Recruiter Inquiries**: View messages, change status (`NEW`, `READ`, `RESPONDED`, `ARCHIVED`), and trigger quick email responses.
- **Biometric Attendance Logs**: Live audit feed of all facial recognition entries with match confidence and device IDs.
- **Profile & Master Security**: Update candidate info (CGPA, college, social URLs) and change administrator master password.

---

## 📡 API Endpoint Reference

### 1. System Health
- `GET http://127.0.0.1:5000/api/health`
- Returns status of both Flask and FastAPI microservices.

### 2. Contact Inquiries (Flask + SQLite)
- `POST http://127.0.0.1:5000/api/contact/submit`
  ```json
  {
    "name": "Alex Johnson",
    "email": "alex@company.com",
    "subject": "Interview Opportunity",
    "message": "We reviewed your portfolio and would love to schedule a technical discussion."
  }
  ```
- `GET http://127.0.0.1:5000/api/contact/messages`

### 3. NLP Email Spam Detection (Flask Gateway -> FastAPI)
- `POST http://127.0.0.1:5000/api/spam/predict`
  ```json
  {
    "email_text": "Congratulations! You won a $1,000,000 lottery cash prize! Claim your bitcoin wire transfer now!"
  }
  ```

### 4. Biometric Face Attendance (Flask Gateway -> FastAPI + SQLite)
- `POST http://127.0.0.1:5000/api/attendance/verify-and-log`
  ```json
  {
    "student_id": "CSE2026-001",
    "student_name": "Pemmasani Tejaswini"
  }
  ```
- `GET http://127.0.0.1:5000/api/attendance/records`

### 5. Dynamic Procedural CAPTCHA (Flask Gateway -> FastAPI)
- `GET http://127.0.0.1:5000/api/captcha/generate`
- `POST http://127.0.0.1:5000/api/captcha/verify`
  ```json
  {
    "captcha_token": "<token_from_generate>",
    "user_solution": "7K9M2P"
  }
  ```

### 6. Clinical Disease Prediction (Flask Gateway -> FastAPI)
- `POST http://127.0.0.1:5000/api/disease/predict-diabetes`
  ```json
  {
    "glucose": 140.0,
    "blood_pressure": 85.0,
    "bmi": 31.2,
    "age": 48
  }
  ```
- `POST http://127.0.0.1:5000/api/disease/predict-heart`
  ```json
  {
    "age": 58,
    "sex": 1,
    "chest_pain_type": 0,
    "resting_bp": 145.0,
    "cholesterol": 250.0,
    "max_heart_rate": 115.0,
    "st_depression": 2.2
  }
  ```

### 7. AI Assistant Q&A Bot (Flask Gateway -> FastAPI)
- `POST http://127.0.0.1:5000/api/assistant/chat`
  ```json
  {
    "query": "What projects has Tejaswini developed in Python?"
  }
  ```
