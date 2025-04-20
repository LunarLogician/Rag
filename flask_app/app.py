from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from docx import Document
import fitz  # PyMuPDF for PDF
import os
import tempfile
import langid  # 🔥 Add this for language detection

def is_english(text):
    lang, _ = langid.classify(text)
    return lang == "en"


app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load ClimateBERT models
commitment_model = AutoModelForSequenceClassification.from_pretrained(
    "climatebert/distilroberta-base-climate-commitment"
)
specificity_model = AutoModelForSequenceClassification.from_pretrained(
    "climatebert/distilroberta-base-climate-specificity"
)

commitment_tokenizer = AutoTokenizer.from_pretrained(
    "climatebert/distilroberta-base-climate-commitment"
)
specificity_tokenizer = AutoTokenizer.from_pretrained(
    "climatebert/distilroberta-base-climate-specificity"
)

# Helper: extract text from DOCX

def extract_text_from_docx(file_stream):
    document = Document(file_stream)
    return "\n".join([para.text for para in document.paragraphs])

# Helper: extract text from PDF using PyMuPDF

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

# Upload endpoint: accepts .docx and .pdf
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    if not (filename.endswith(".docx") or filename.endswith(".pdf")):
        return jsonify({"error": "Unsupported file type. Please upload a PDF or Word document (.pdf, .docx)"}), 400

    try:
        if filename.endswith(".docx"):
            text = extract_text_from_docx(file.stream)
        else:
            # Save to temp file to read PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            text = extract_text_from_pdf(tmp_path)
            os.remove(tmp_path)

    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500

    return jsonify({"name": filename, "text": text})

# Analysis endpoint
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    if not is_english(text):  # 🔥 Add this check
        return jsonify({"error": "Non-English text detected. Only English documents are supported."}), 400

    commitment_score = get_score(commitment_model, commitment_tokenizer, text)
    specificity_score = get_score(specificity_model, specificity_tokenizer, text)
    cheap_talk_score = commitment_score * (1 - specificity_score)
    safe_talk_score = (1 - commitment_score) * specificity_score

    return jsonify({
        "commitment_probability": commitment_score,
        "specificity_probability": specificity_score,
        "cheap_talk_probability": cheap_talk_score,
        "safe_talk_probability": safe_talk_score
    })


# Model scoring helper
def get_score(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return probs[0, 1].item()

if __name__ == '__main__':
    app.run(debug=True, port=5001)