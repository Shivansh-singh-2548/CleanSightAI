from flask import Flask, render_template, request, send_from_directory
import os
import sqlite3

from ai_model import analyze_waste


app = Flask(__name__)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = sqlite3.connect("cleansight.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT,
            waste_type TEXT,
            description TEXT,
            location TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# SEVERITY CALCULATION
# =========================================================

def calculate_severity(description):

    text = description.lower()

    high_words = [
        "overflow",
        "overflowing",
        "large",
        "huge",
        "massive",
        "dump",
        "dumped",
        "pile",
        "dangerous"
    ]

    medium_words = [
        "lot",
        "many",
        "moderate",
        "dirty",
        "scattered"
    ]

    # High severity

    for word in high_words:

        if word in text:
            return "High"

    # Medium severity

    for word in medium_words:

        if word in text:
            return "Medium"

    # Default

    return "Low"


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REPORT SUBMISSION
# =========================================================

@app.route("/report", methods=["POST"])
def report():

    # -----------------------------------------------------
    # Get form data
    # -----------------------------------------------------

    image = request.files["image"]

    user_waste_type = request.form["waste_type"]

    description = request.form["description"]

    location = request.form["location"]


    # -----------------------------------------------------
    # Save uploaded image
    # -----------------------------------------------------

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

    image.save(image_path)


    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    print("\n================ AI ANALYSIS ================")

    # Get ALL AI predictions
    ai_results = analyze_waste(image_path)

    # First prediction = highest confidence
    best_result = ai_results[0]

    ai_waste_type = best_result["label"]

    confidence = best_result["score"]


    print(
        "AI Waste Type:",
        ai_waste_type
    )

    print(
        "AI Confidence:",
        round(confidence * 100, 2),
        "%"
    )

    print("\nAll AI Predictions:")

    for result in ai_results:

        print(
            result["label"],
            "->",
            round(result["score"] * 100, 2),
            "%"
        )

    print("=============================================")


    # -----------------------------------------------------
    # CALCULATE SEVERITY
    # -----------------------------------------------------

    severity = calculate_severity(description)

    print(
        "Severity:",
        severity
    )


    # -----------------------------------------------------
    # SAVE REPORT TO DATABASE
    # -----------------------------------------------------

    conn = sqlite3.connect("cleansight.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (
            image,
            waste_type,
            description,
            location,
            severity
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        image.filename,
        ai_waste_type,
        description,
        location,
        severity
    ))

    conn.commit()

    print("REPORT SAVED TO DATABASE")

    conn.close()


    # -----------------------------------------------------
    # TERMINAL INFORMATION
    # -----------------------------------------------------

    print("Image:", image.filename)

    print(
        "User Selected Waste Type:",
        user_waste_type
    )

    print(
        "AI Waste Type:",
        ai_waste_type
    )

    print(
        "Description:",
        description
    )

    print(
        "Location:",
        location
    )

    print(
        "Severity:",
        severity
    )


    # -----------------------------------------------------
    # SHOW RESULT PAGE
    # -----------------------------------------------------

    return render_template(

        "report.html",

        image=image.filename,

        waste_type=ai_waste_type,

        description=description,

        location=location,

        confidence=round(
            confidence * 100,
            2
        ),

        # Send ALL predictions to HTML
        ai_results=ai_results,

        severity=severity

    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("cleansight.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    # -----------------------------------------------------
    # Get all reports
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()


    # -----------------------------------------------------
    # Total reports
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM reports
    """)

    total_reports = cursor.fetchone()[0]


    # -----------------------------------------------------
    # Plastic reports
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM reports
        WHERE LOWER(waste_type) = 'plastic'
    """)

    plastic_reports = cursor.fetchone()[0]


    # -----------------------------------------------------
    # Pending reports
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM reports
        WHERE severity = 'Pending'
    """)

    pending_reports = cursor.fetchone()[0]


    conn.close()


    # -----------------------------------------------------
    # Show dashboard
    # -----------------------------------------------------

    return render_template(

        "dashboard.html",

        reports=reports,

        total_reports=total_reports,

        plastic_reports=plastic_reports,

        pending_reports=pending_reports

    )


# =========================================================
# SERVE UPLOADED IMAGES
# =========================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)