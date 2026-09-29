# CleanSight AI 

### See the Problem. Clean the Future.

CleanSight AI is a web-based waste reporting system designed to help communities identify and report waste problems using images and structured information.

The project combines a simple web interface with a Python Flask backend to collect waste reports, upload images, and store report information for further AI-based analysis.

---

##  Project Overview

Waste problems such as plastic dumping, mixed waste, roadside garbage, and improper disposal can be difficult to track and manage.

CleanSight AI aims to make waste reporting easier by allowing users to:

-  Upload an image of a waste problem
-  Select the type of waste
-  Describe the problem
-  Enter the location
- Analyze the problem using AI/ML
-  Generate useful insights and reports

The current version focuses on building the working web application and backend foundation.

---

##  Features

### Currently Implemented

- Responsive web interface
- CleanSight AI landing page
- Waste reporting form
- Image upload
- Flask backend
- Form data handling
- Uploaded image storage
- Waste type collection
- Description collection
- Location collection

### Planned Features

- AI-based waste classification
- Waste severity estimation
- Confidence score
- Automated recommendations
- SQLite database for reports
- Report history
- Dashboard and analytics
- Waste hotspot identification
- Collection priority estimation
- Before/after comparison

---

##  Tech Stack

### Frontend

- HTML5
- CSS3
- Bootstrap *(if used in future versions)*

### Backend

- Python
- Flask

### AI / Machine Learning

Planned:

- NumPy
- Pandas
- Matplotlib
- Scikit-learn
- Computer Vision
- Machine Learning models

### Database

Planned:

- SQLite
- SQL

---

##  Project Structure

```text
CleanSight-AI/
│
├── app.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── uploads/
│   └── uploaded images
│
└── README.md
