from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
from transformers import pipeline

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def split_text_into_chunks(text, max_length):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_pdf(pdf_path):
    summarizer = pipeline("summarization")
    print(summarizer.model.config)
    try:
        full_text = extract_text_from_pdf(pdf_path)
        chunks = split_text_into_chunks(full_text, 1024)
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, min_length=40, do_sample=False)[0]['summary_text']
            summaries.append(summary)

        final_summary = " ".join(summaries)
        image_summary = "No images found"
        
        return final_summary, image_summary
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summari', methods=['POST'])
def summari():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file:    
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            pdf_path = os.path.join('uploads', filename)
            summary, image_summary = process_pdf(pdf_path)
            if summary:
                return jsonify({'summary': summary})
            else:
                return jsonify({'error': 'Error processing PDF'})

@app.route('/sum')
def summary():
    return render_template('sum.html')

@app.route('/abt')
def about():
    return render_template('abt.html')

@app.route('/hom')
def home():
    return render_template('index.html')

@app.route('/con')
def contact():
    return render_template('con.html')

if __name__ == '__main__':
    app.run(debug=False)