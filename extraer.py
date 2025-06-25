from flask import Flask, render_template, request, send_file
import PyPDF2
from fpdf import FPDF
import io
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from docx import Document
from docx2pdf import convert as docx2pdf_convert
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pdf_to_word', methods=['GET', 'POST'])
def pdf_to_word():
    error = ""
    if request.method == 'POST':
        file = request.files['pdf']
        if file and file.filename.endswith('.pdf'):
            try:
                file_bytes = file.read()
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += page_text + "\n"
                if not text.strip():
                    images = convert_from_bytes(file_bytes)
                    for img in images:
                        ocr_text = pytesseract.image_to_string(img, lang='spa+eng')
                        text += ocr_text + "\n"
                if not text.strip():
                    error = "No se pudo extraer texto del PDF."
                    return render_template('pdf_to_word.html', error=error)
                # Crear documento Word
                doc = Document()
                for line in text.split('\n'):
                    doc.add_paragraph(line)
                temp_word = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
                doc.save(temp_word.name)
                temp_word.seek(0)
                return send_file(temp_word.name, as_attachment=True, download_name="convertido.docx", mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            except Exception as e:
                print("ERROR:", e)
                error = "Error al convertir PDF a Word."
        else:
            error = "Archivo no válido."
    return render_template('pdf_to_word.html', error=error)

@app.route('/word_to_pdf', methods=['GET', 'POST'])
def word_to_pdf():
    error = ""
    if request.method == 'POST':
        file = request.files['word']
        if file and file.filename.endswith('.docx'):
            try:
                temp_word = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
                file.save(temp_word.name)
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                docx2pdf_convert(temp_word.name, temp_pdf.name)
                temp_pdf.seek(0)
                return send_file(temp_pdf.name, as_attachment=True, download_name="convertido.pdf", mimetype='application/pdf')
            except Exception as e:
                print("ERROR:", e)
                error = "Error al convertir Word a PDF."
        else:
            error = "Archivo no válido."
    return render_template('word_to_pdf.html', error=error)

@app.route('/extractor', methods=['GET', 'POST'])
def index():
    text = ""
    if request.method == 'POST':
        file = request.files['pdf']
        if file and file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    return render_template('extractor.html', text=text)

@app.route('/terminos_condiciones')
def terminos_condiciones():
    return render_template('terminos_condiciones.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
