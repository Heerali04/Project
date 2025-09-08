import os
import re
import pytesseract
import fitz
from datetime import datetime
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

# ML imports
import joblib
import pandas as pd
import numpy as np

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
users_collection = db["users"]
reports_collection = db["reports"]

# Indexes
reports_collection.create_index("disease")
reports_collection.create_index("created_at")
reports_collection.create_index("user_id")

# ---------------- Helpers ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_suggestions(disease, result):
    """Return suggestions only for positive / detected / possible results"""
    result_lower = result.lower().strip()

    if result_lower in ["negative", "not detected", "unknown"]:
        return None  

    if result_lower in ["positive", "detected", "possible"]:
        if "nipah" in disease.lower():
            return "Seek immediate medical attention and follow strict isolation protocols."
        elif "rabies" in disease.lower():
            return "Emergency medical treatment is required. Contact a doctor immediately."
        elif "dengue" in disease.lower():
            return "Consult a physician for proper diagnosis and management of symptoms. Stay hydrated."
        else:
            return "Possible zoonotic disease detected. Consult a healthcare professional."

    return None

def save_report(report_entry):
    try:
        result = reports_collection.insert_one(report_entry.copy())
        return str(result.inserted_id)
    except Exception as e:
        raise RuntimeError(f"Failed to save report: {str(e)}")

def serialize_report(report):
    report["_id"] = str(report["_id"])
    return report

# ---------------- Load ML Models ----------------
try:
    xgb_model = joblib.load("xgboost_disease_model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    print("✅ XGBoost + LabelEncoder loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load ML models - {e}")
    xgb_model, label_encoder = None, None

# ---------------- Auth Routes ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_pw})
    return jsonify({"success": True, "message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

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

        text = ""
        if filename.lower().endswith(".pdf"):
            with fitz.open(file_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    if not page_text.strip():
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        page_text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")
                    text += page_text
        else:
            text = pytesseract.image_to_string(Image.open(file_path), config="--oem 3 --psm 6")

        disease_match = re.search(r"(Dengue|Nipah|Rabies|Zoonotic)", text, re.IGNORECASE)
        disease = disease_match.group(1) if disease_match else "Unknown"

        result_match = re.search(
            r"(not\s+detected|negative|positive|detected|unclear)",
            text,
            re.IGNORECASE,
        )
        if result_match:
            result_raw = result_match.group(1).lower().strip()
            if "not detected" in result_raw or result_raw == "negative":
                result = "Negative"
            elif result_raw in ["positive", "detected"]:
                result = "Positive"
            elif "unclear" in result_raw:
                result = "Unclear"
            else:
                result = "Unknown"
        else:
            result = "Unknown"

        ct_match = re.search(r"Ct\s*=?\s*(\d+(\.\d+)?)", text, re.IGNORECASE)
        ct_value = ct_match.group(1) if ct_match else "N/A"

        suggestion = get_suggestions(disease, result)

        report_entry = {
            "disease": disease,
            "result": result,
            "ct_value": ct_value,
            "suggestion": suggestion,
            "raw_text": text,
            "created_at": datetime.utcnow(),
            "source": "upload"
        }

        inserted_id = save_report(report_entry)
        report_entry["id"] = inserted_id
        return jsonify(report_entry)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ---------------- Symptom Prediction ----------------
@app.route("/predict_symptoms", methods=["POST"])
def predict_symptoms():
    if xgb_model is None or label_encoder is None:
        return jsonify({"error": "ML model not loaded"}), 500

    data = request.get_json()
    input_symptoms = data.get("symptoms", "").lower().split(",")
    input_symptoms = [s.strip() for s in input_symptoms if s.strip()]

    # ✅ Synonym mapping
    synonym_map = {
        "bodyache": "muscle pain",
        "fear of water": "hydrophobia",
        "breathing": "respiratory distress",
        "respiratory": "respiratory distress",
        "dog": "animal contact",
        "animal": "animal contact",
        "scratch": "bite",
        "pain": "joint pain",
        "chills": "fever",
    }

    normalized_symptoms = [synonym_map.get(s, s) for s in input_symptoms]

    # ✅ Features from training
    feature_names = [
        "anxiety", "bite", "muscle pain", "saliva", "hallucination",
        "seizure", "respiratory distress", "rash", "paralysis", "headache",
        "bleeding", "hydrophobia", "cold", "fever", "joint pain",
        "encephalitis", "agitation", "animal contact", "nausea",
        "confusion", "cough", "vomiting"
    ]

    X = pd.DataFrame(
        [[1 if f in normalized_symptoms else 0 for f in feature_names]],
        columns=feature_names
    )

    # ✅ Prediction
    prediction_enc = xgb_model.predict(X)[0]
    prediction = label_encoder.inverse_transform([prediction_enc])[0]

    # ✅ Confidence calculation
    try:
        proba = xgb_model.predict_proba(X)[0]
        confidence = float(np.max(proba)) * 100
        confidence = round(confidence , 2)
    except Exception as e:
        print("⚠️ Confidence error:", e)
        confidence = 0.0

    matched = [s for s in normalized_symptoms if s in feature_names]

    report_entry = {
        "symptoms": data.get("symptoms", ""),
        "prediction": prediction,
        "matched_symptoms": matched,
        "confidence": confidence,
        "suggestion": get_suggestions(prediction, "possible") if confidence > 50 else None,
        "created_at": datetime.utcnow(),
        "source": "ml-symptoms"
    }

    save_report(report_entry)
    return jsonify(report_entry)


# ---------------- Reports History ----------------
@app.route("/reports", methods=["GET"])
def get_reports():
    try:
        data = [serialize_report(r) for r in reports_collection.find()]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ---------------- Clear Reports ----------------
@app.route("/clear_reports", methods=["DELETE"])
def clear_reports():
    try:
        reports_collection.delete_many({})  # deletes all documents
        return jsonify({"success": True, "message": "All reports cleared."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
