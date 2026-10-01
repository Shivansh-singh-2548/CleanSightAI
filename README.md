# CleanSight AI

### See the Problem. Clean the Future.

CleanSight AI is an AI-assisted waste reporting and monitoring web application.

The system allows users to upload an image of a waste problem, provide a description and location, and receive AI-based waste classification results. Reports are stored in a database and displayed through a monitoring dashboard.

---

## Features

- Upload waste images
- AI-based waste classification
- Multiple AI predictions with confidence scores
- Preliminary waste severity calculation
- Location-based reporting
- Waste problem description
- SQLite database for storing reports
- Dashboard for monitoring submitted reports
- Display uploaded waste images
- Flask-based web application

---

## How It Works

```text
User
  |
  v
Upload Waste Image
  |
  v
Flask Backend
  |
  v
AI Image Classification
  |
  v
Waste Predictions + Confidence
  |
  v
Severity Calculation
  |
  v
SQLite Database
  |
  v
Report Result
  |
  v
Dashboard
