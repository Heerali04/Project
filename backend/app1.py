import os
import re
import pytesseract
import fitz
import tempfile
import difflib
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

# ---------------- Flask Setup ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

# ---------------- Database Setup (MongoDB) ----------------
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["zoonotic_ai"]
users_collection = db["users"]     # user accounts
reports_collection = db["reports"] # test/symptom reports

# ---------------- Helpers ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def fuzzy_find(word, text):
    words = text.lower().split()
    match = difflib.get_close_matches(word, words, n=1, cutoff=0.7)
    return bool(match)

def get_suggestions(disease, result):
    if result.lower() in ["positive", "possible"]:
        if "nipah" in disease.lower():
            return "Seek immediate medical attention and follow strict isolation protocols."
        elif "rabies" in disease.lower():
            return "Emergency medical treatment is required. Contact a doctor immediately."
        elif "dengue" in disease.lower():
            return "Consult a physician for proper diagnosis and management of symptoms. Stay hydrated."
        else:
            return "Possible zoonotic disease detected. Consult a healthcare professional."
    return "Test result is negative or unclear. Continue to monitor symptoms."

def save_report(report_entry):
    """Insert report into MongoDB"""
    try:
        result = reports_collection.insert_one(report_entry.copy())  # copy so original dict not altered
        return str(result.inserted_id)  # return id as string if needed
    except Exception as e:
        raise RuntimeError(f"Failed to save report: {str(e)}")


# ---------------- Auth Routes ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    try:
        if users_collection.find_one({"username": username}):
            return jsonify({"success": False, "message": "Username already exists"}), 400

        hashed_pw = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_pw})
        return jsonify({"success": True, "message": "User registered successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    try:
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            return jsonify({"success": True, "message": "Login successful"})
        return jsonify({"success": False, "message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ---------------- File Upload / OCR ----------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        file.save(file_path)
        print(f"✅ File saved: {file_path}")   # DEBUG

        text = ""

        # --- Extract text ---
        if filename.lower().endswith(".pdf"):
            # Direct text extraction for ReportLab PDFs
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += page.get_text()
        else:
            # OCR fallback for images
            config = r"--oem 3 --psm 6"
            text = pytesseract.image_to_string(Image.open(file_path), config=config)

        print(f"✅ Extracted text (first 200 chars): {text[:200]}")  # DEBUG

        # --- Regex extraction ---
        disease_match = re.search(r"(Dengue|Nipah|Rabies|Zoonotic)", text, re.IGNORECASE)
        result_match = re.search(r"Overall result:\s*(Positive|Negative)", text, re.IGNORECASE)

        # Capture Ct values in two formats
        ct_values = {}

        # Format 1: Inline style "(Ct = 23.5)"
        matches_format1 = re.findall(
            r"([A-Za-z0-9]+ gene).*?\(Ct\s*=?\s*([\d.]+)\)",
            text,
            re.IGNORECASE
        )

        # Format 2: Table style ("N gene Detected 23.8")
        matches_format2 = re.findall(
            r"(NS1 gene|E gene|N gene|G gene)\s+Detected\s+([\d.]+)",
            text,
            re.IGNORECASE
        )

        for gene, value in matches_format1 + matches_format2:
            ct_values[gene.strip()] = value

        disease = disease_match.group(1) if disease_match else "Unknown"
        result = result_match.group(1) if result_match else "Unknown"

        suggestion = get_suggestions(disease, result)

        report_entry = {
            "disease": disease,
            "result": result,
            "ct_values": ct_values if ct_values else "N/A",
            "ct_value": ", ".join([f"{g}: {v}" for g, v in ct_values.items()]) if ct_values else "N/A",
            "suggestion": suggestion,
            "raw_text": text,
        }

        inserted_id = save_report(report_entry)
        report_entry["id"] = inserted_id  # optional, as string
        return jsonify(report_entry)

    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")  # DEBUG
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ---------------- Symptoms Entry ----------------
@app.route("/symptoms", methods=["POST"])
def analyze_symptoms():
    data = request.json
    symptoms_text = data.get("symptoms", "").lower()

    if not symptoms_text.strip():
        return jsonify({"error": "No symptoms provided"}), 400

    symptoms_words = symptoms_text.split()
    disease_keywords = {
        "Dengue": ["fever", "headache", "rash", "pain", "vomiting"],
        "Rabies": ["bite", "dog", "animal", "saliva", "scratch"],
        "Nipah": ["respiratory", "cough", "encephalitis", "seizure", "confusion", "cold"],
    }

    results = []
    for disease, keywords in disease_keywords.items():
        matches = [w for w in keywords if any(word.startswith(w[:3]) for word in symptoms_words)]
        if matches:
            results.append({
                "disease": disease,
                "matched_symptoms": matches,
                "count": len(matches),
                "result": "Possible",
                "suggestion": get_suggestions(disease, "Possible"),
            })

    if not results:
        results = [{
            "disease": "Unknown",
            "matched_symptoms": [],
            "count": 0,
            "result": "Unclear",
            "suggestion": "Symptoms do not match known patterns. Please consult a healthcare professional.",
        }]

    report_entry = {
        "symptoms": symptoms_text,
        "possible_diseases": results,
    }

    save_report(report_entry)
    return jsonify(report_entry)

# ---------------- Reports History ----------------
@app.route("/reports", methods=["GET"])
def get_reports():
    try:
        data = list(reports_collection.find({}, {"_id": 0}))  # exclude MongoDB _id field
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
