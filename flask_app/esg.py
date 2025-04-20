from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from docx import Document
import fitz  # PyMuPDF for PDF
import os
import tempfile
import langid  # 🔥 Add this for language detection

def is_english(text: str) -> bool:
    lang, _ = langid.classify(text)
    return lang == "en"

app = Flask(__name__)
CORS(app)

# These will be initialized inside `main` safely
esg_tokenizer = None
esg_model = None
nlp = None

categories = [
    'Business Ethics & Values', 'Climate Change', 'Community Relations',
    'Corporate Governance', 'Human Capital', 'Natural Capital', 'Non-ESG',
    'Pollution & Waste', 'Product Liability'
]

def extract_text_from_docx(file_stream):
    document = Document(file_stream)
    return "\n".join([para.text for para in document.paragraphs])

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

def chunk_text(text, word_limit):
    words = text.split()
    return [' '.join(words[i:i + word_limit]) for i in range(0, len(words), word_limit)]

def truncate_text(text, tokenizer, max_length=512):
    tokens = tokenizer(text, truncation=True, max_length=max_length, return_tensors='pt')
    return tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)

def get_avg_predictions(text_chunks, nlp, tokenizer, categories):
    total_predictions = {category: 0 for category in categories}
    chunk_count = len(text_chunks)
    for chunk in text_chunks:
        truncated_chunk = truncate_text(chunk, tokenizer)
        predictions = nlp(truncated_chunk)
        for pred in predictions:
            for score in pred:
                total_predictions[score['label']] += score['score']
    return {category: total / chunk_count for category, total in total_predictions.items()}

@app.route("/esg", methods=["POST"])
def esg_analysis():
    global esg_tokenizer, nlp
    data = request.json
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    if not is_english(text):  # 🔥 Reject non-English
        return jsonify({"error": "Non-English text detected. Only English documents are supported."}), 400

    chunks = chunk_text(text, 1500)
    avg_predictions = get_avg_predictions(chunks, nlp, esg_tokenizer, categories)
    return jsonify(avg_predictions)

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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            text = extract_text_from_pdf(tmp_path)
            os.remove(tmp_path)
    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500

    return jsonify({"name": filename, "text": text})

if __name__ == "__main__":
    from transformers.utils import logging
    logging.set_verbosity_error()

    print("Loading FinBERT ESG model...")
    esg_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-esg-9-categories")
    esg_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-esg-9-categories")
    nlp = pipeline("text-classification", model=esg_model, tokenizer=esg_tokenizer, top_k=None)

    print("Model loaded. Running server on http://localhost:5002")
    app.run(debug=True, port=5002)
