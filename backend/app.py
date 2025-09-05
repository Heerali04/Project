import os
import re
import json
import pytesseract
import fitz
import sqlite3
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import tempfile
import difflib

# ---------------- Flask Setup ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

REPORTS_FILE = "reports.json"

# ---------------- Database Setup ----------------
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()

init_db()

# ---------------- Helpers ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def fuzzy_find(word, text):
    words = text.lower().split()
    match = difflib.get_close_matches(word, words, n=1, cutoff=0.7)
    return bool(match)

def get_suggestions(disease, result):
    if result.lower() == "positive":
        if "nipah" in disease.lower():
            return "Seek immediate medical attention and follow strict isolation protocols."
        elif "rabies" in disease.lower():
            return "Emergency medical treatment is required. Contact a doctor immediately."
        elif "dengue" in disease.lower():
            return "Consult a physician for proper diagnosis and management of symptoms. Stay hydrated."
        else:
            return "Test positive for an unspecified zoonotic disease. Consult a healthcare professional."
    return "Test result is negative. Continue to monitor symptoms."

# ---------------- Auth Routes ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists"}), 400
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[0], password):
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
        text = ""
        config = r"--oem 3 --psm 6"

        if filename.lower().endswith(".pdf"):
            with fitz.open(file_path) as doc:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap()
                        img_path = os.path.join(temp_dir, f"page_{page_num}.png")
                        pix.save(img_path)
                        text += pytesseract.image_to_string(Image.open(img_path), config=config)
        else:
            text = pytesseract.image_to_string(Image.open(file_path), config=config)

        disease_match = re.search(r"\b(Nipah|Rabies|Dengue|Zoonotic)\b", text, re.IGNORECASE)
        ct_match = re.search(r"\(?C\s?t(?:\s*Value)?\s*[:=]?\s*(\d+(\.\d+)?)\)?", text, re.IGNORECASE)

        disease = disease_match.group(1) if disease_match else "Unknown"
        result = "Positive" if fuzzy_find("positive", text) else "Negative" if fuzzy_find("negative", text) else "Unknown"
        ct_value = ct_match.group(1) if ct_match else "N/A"
        suggestion = get_suggestions(disease, result)

        report_entry = {
            "disease": disease,
            "result": result,
            "ct_value": ct_value,
            "suggestion": suggestion,
        }

        try:
            with open(REPORTS_FILE, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(report_entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except Exception as e:
            return jsonify({"error": f"Failed to save report: {str(e)}"}), 500

        return jsonify({**report_entry, "raw_text": text})

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ---------------- Reports ----------------
@app.route("/reports", methods=["GET"])
def get_reports():
    try:
        with open(REPORTS_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
