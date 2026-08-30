import os, uuid
from flask import Flask, render_template, request, jsonify
from PIL import Image
import pytesseract
from scanner import analyze_sms

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
ALLOWED = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "Walang image na natanggap."}), 400

    f = request.files["image"]
    if not f.filename or not allowed_file(f.filename):
        return jsonify({"error": "PNG, JPG, JPEG, o WEBP lamang ang supported."}), 400

    try:
        image = Image.open(f.stream).convert("RGB")
        extracted_text = pytesseract.image_to_string(image, lang="eng")
        extracted_text = extracted_text.strip()

        if not extracted_text:
            return jsonify({
                "error": "Walang mabasang text. Gumamit ng mas malinaw na screenshot."
            }), 400

        result = analyze_sms(extracted_text)
        return jsonify({
            "success": True,
            "extracted_text": extracted_text,
            **result
        })
    except pytesseract.TesseractNotFoundError:
        return jsonify({
            "error": "Hindi makita ang Tesseract OCR. I-install muna ang Tesseract at idagdag sa PATH."
        }), 500
    except Exception as e:
        return jsonify({"error": f"May error sa pag-analyze: {str(e)}"}), 500

@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Maglagay ng SMS text."}), 400
    result = analyze_sms(text)
    return jsonify({"success": True, "extracted_text": text, **result})

if __name__ == "__main__":
    app.run(debug=True)
