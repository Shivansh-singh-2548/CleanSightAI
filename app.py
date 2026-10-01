from flask import Flask, render_template, request, send_from_directory
import os
import sqlite3

app = Flask(__name__)


# ================= UPLOAD FOLDER =================

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DATABASE =================

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


# ================= HOME =================

@app.route("/")
def home():

    return render_template("index.html")


# ================= REPORT =================

@app.route("/report", methods=["POST"])
def report():

    # Get image
    image = request.files["image"]

    # Get form data
    waste_type = request.form["waste_type"]
    description = request.form["description"]
    location = request.form["location"]


    # ================= SAVE IMAGE =================

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

    image.save(image_path)


    # ================= SAVE TO DATABASE =================

    conn = sqlite3.connect("cleansight.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (image, waste_type, description, location, severity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        image.filename,
        waste_type,
        description,
        location,
        "Pending"
    ))

    conn.commit()

    print("REPORT SAVED TO DATABASE")

    conn.close()


    # ================= TERMINAL OUTPUT =================

    print("Image:", image.filename)
    print("Waste Type:", waste_type)
    print("Description:", description)
    print("Location:", location)


    # ================= REPORT PAGE =================

    return render_template(
        "report.html",
        image=image.filename,
        waste_type=waste_type,
        description=description,
        location=location
    )


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("cleansight.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reports
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        reports=reports
    )


# ================= UPLOADED IMAGES =================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ================= START APP =================

init_db()


if __name__ == "__main__":

    app.run(debug=True)