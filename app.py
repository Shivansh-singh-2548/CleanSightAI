from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["POST"])
def report():

    # Get image
    image = request.files["image"]

    # Get other form data
    waste_type = request.form["waste_type"]
    description = request.form["description"]
    location = request.form["location"]

    # Save image
    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

    image.save(image_path)

    print("Image:", image.filename)
    print("Waste Type:", waste_type)
    print("Description:", description)
    print("Location:", location)

    return "Report received successfully!"


if __name__ == "__main__":
    app.run(debug=True)