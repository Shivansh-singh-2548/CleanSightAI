import os
import sqlite3
from uuid import uuid4

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)

from werkzeug.utils import secure_filename

from ai_model import analyze_waste


# --------------------------------------------------
# FLASK CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE = os.path.join(BASE_DIR, "cleansight.db")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# --------------------------------------------------
# INITIALIZE DATABASE AND MIGRATE EXISTING DATABASE
# --------------------------------------------------

def init_db():

    conn = get_db_connection()

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

    # Read existing columns.

    cursor.execute("PRAGMA table_info(reports)")

    existing_columns = {
        column["name"]
        for column in cursor.fetchall()
    }

    # Add latitude if it does not already exist.

    if "latitude" not in existing_columns:

        cursor.execute("""
            ALTER TABLE reports
            ADD COLUMN latitude REAL
        """)

    # Add longitude if it does not already exist.

    if "longitude" not in existing_columns:

        cursor.execute("""
            ALTER TABLE reports
            ADD COLUMN longitude REAL
        """)

    conn.commit()

    conn.close()

    print("Database initialized successfully.")


# --------------------------------------------------
# SEVERITY CALCULATION
# --------------------------------------------------

def calculate_severity(description):

    description = description.lower()

    high_keywords = [
        "overflow",
        "overflowing",
        "large",
        "huge",
        "massive",
        "dump",
        "dumped",
        "pile",
        "dangerous",
    ]

    medium_keywords = [
        "lot",
        "many",
        "moderate",
        "dirty",
        "scattered",
    ]

    if any(word in description for word in high_keywords):
        return "High"

    if any(word in description for word in medium_keywords):
        return "Medium"

    return "Low"


# --------------------------------------------------
# IMAGE VALIDATION
# --------------------------------------------------

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# SUBMIT WASTE REPORT
# --------------------------------------------------

@app.route("/report", methods=["POST"])
def report():

    image = request.files.get("image")

    user_waste_type = request.form.get(
        "waste_type", ""
    ).strip()

    description = request.form.get(
        "description", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    latitude_text = request.form.get(
        "latitude", ""
    ).strip()

    longitude_text = request.form.get(
        "longitude", ""
    ).strip()


    # Validate required fields.

    if (
        image is None
        or image.filename == ""
        or not description
        or not location
        or not user_waste_type
    ):

        return "Please complete all required fields.", 400


    if not allowed_file(image.filename):

        return (
            "Unsupported image format. Use JPG, JPEG or PNG.",
            400,
        )


    # Validate coordinates.

    try:

        latitude = float(latitude_text)

        longitude = float(longitude_text)

    except (TypeError, ValueError):

        return (
            "Please select a valid location on the map.",
            400,
        )


    # Ensure coordinates are valid geographic values.

    if not (-90 <= latitude <= 90):

        return "Invalid latitude.", 400

    if not (-180 <= longitude <= 180):

        return "Invalid longitude.", 400


    # Save uploaded image with a unique filename.

    original_filename = secure_filename(image.filename)

    extension = original_filename.rsplit(".", 1)[1].lower()

    image_filename = f"{uuid4().hex}.{extension}"

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image_filename,
    )

    image.save(image_path)


    # --------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------

    try:

        ai_results = analyze_waste(image_path)

        if not ai_results:

            raise ValueError("The AI model returned no predictions.")

        best_result = ai_results[0]

        ai_waste_type = best_result["label"]

        confidence = best_result["score"]

    except Exception:

        # Do not save a report as if AI analysis succeeded
        # when the model failed.

        if os.path.exists(image_path):
            os.remove(image_path)

        app.logger.exception("AI image analysis failed.")

        return (
            "AI analysis failed. Please try another image.",
            500,
        )


    # --------------------------------------------------
    # SEVERITY
    # --------------------------------------------------

    severity = calculate_severity(description)


    # --------------------------------------------------
    # SAVE REPORT IN SQLITE
    # --------------------------------------------------

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reports (
                image,
                waste_type,
                description,
                location,
                severity,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            image_filename,
            ai_waste_type,
            description,
            location,
            severity,
            latitude,
            longitude,
        ))

        conn.commit()

    finally:

        conn.close()


    # --------------------------------------------------
    # DISPLAY REPORT RESULT
    # --------------------------------------------------

    return render_template(
        "report.html",

        image=image_filename,

        waste_type=ai_waste_type,

        description=description,

        location=location,

        confidence=round(confidence * 100, 2),

        ai_results=ai_results,

        severity=severity,

        latitude=latitude,

        longitude=longitude,

        user_waste_type=user_waste_type,
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()


    # Total reports.

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
    """)

    total_reports = cursor.fetchone()["total"]


    # Plastic reports.

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE LOWER(waste_type) = 'plastic'
    """)

    plastic_reports = cursor.fetchone()["total"]


    # Reports with coordinates.

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
    """)

    mapped_reports = cursor.fetchone()["total"]


    # Severity counts.

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE severity = 'High'
    """)

    high_reports = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE severity = 'Medium'
    """)

    medium_reports = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE severity = 'Low'
    """)

    low_reports = cursor.fetchone()["total"]


    conn.close()


    # Only reports with coordinates can be placed on the map.

    map_reports = []

    for report_item in reports:

        if (
            report_item["latitude"] is not None
            and report_item["longitude"] is not None
        ):

            map_reports.append({

                "id": report_item["id"],

                "latitude": report_item["latitude"],

                "longitude": report_item["longitude"],

                "location": report_item["location"] or "Unknown location",

                "waste_type": report_item["waste_type"] or "Unknown",

                "description": report_item["description"] or "",

                "severity": report_item["severity"] or "Low",

                "image": report_item["image"] or "",

                "created_at": str(report_item["created_at"] or ""),

            })


    return render_template(

        "dashboard.html",

        reports=reports,

        map_reports=map_reports,

        total_reports=total_reports,

        plastic_reports=plastic_reports,

        mapped_reports=mapped_reports,

        high_reports=high_reports,

        medium_reports=medium_reports,

        low_reports=low_reports,

    )


# --------------------------------------------------
# SERVE UPLOADED IMAGES
# --------------------------------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

init_db()


if __name__ == "__main__":

    app.run(debug=True)