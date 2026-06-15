import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pdfplumber

from services.analyzer import analyze_user
from services.groq_client import generate_roadmap, extract_skills_from_resume

app = Flask(__name__)

# ── Upload config ──
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()


# ── Routes ──

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Manual skill entry flow."""
    skills_input = request.form["skills"]
    target_role  = request.form["target_role"]

    user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    result = analyze_user(user_skills, target_role)

    roadmap = generate_roadmap(
        target_role     = result["target_role"],
        readiness_score = result["readiness_score"],
        current_skills  = [s["skill"] for s in result["matched_skills"]],
        critical_gaps   = [s["skill"] for s in result["critical_gaps"]],
    )

    return render_template("result.html", result=result, roadmap=roadmap)


@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    """Resume upload flow."""

    # 1. Validate file
    if "resume" not in request.files:
        return render_template("index.html", error="No file uploaded.")

    file = request.files["resume"]
    target_role = request.form.get("target_role", "Data Analyst")

    if file.filename == "":
        return render_template("index.html", error="No file selected.")

    if not allowed_file(file.filename):
        return render_template("index.html", error="Only PDF files are supported.")

    # 2. Save & extract text
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    resume_text = extract_text_from_pdf(filepath)

    # 3. Extract skills via Groq / Llama 3
    extracted_skills = extract_skills_from_resume(resume_text)

    # 4. Run analysis
    result = analyze_user(extracted_skills, target_role)

    roadmap = generate_roadmap(
        target_role     = result["target_role"],
        readiness_score = result["readiness_score"],
        current_skills  = [s["skill"] for s in result["matched_skills"]],
        critical_gaps   = [s["skill"] for s in result["critical_gaps"]],
    )

    # Clean up uploaded file
    os.remove(filepath)

    return render_template(
        "result.html",
        result=result,
        roadmap=roadmap,
        extracted_skills=extracted_skills,
        from_resume=True
    )


if __name__ == "__main__":
    app.run(debug=True)