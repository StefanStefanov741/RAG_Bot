from Preprocessing.PDF.pdfminer import pdf_to_elements
from Preprocessing.PDF.advanced_pdf import pdf_to_elements_advanced
from flask import Flask, request, jsonify
import json
import uuid
import os

app = Flask(__name__)

tempFolder = "/app/tmp"

def elements_to_json(elements):
    # Create a list of dictionaries for each element
    elements_list = [{"category": element.category, "text": element.text} for element in elements]
    
    # Convert the list to a JSON string
    return json.dumps(elements_list, indent=4)

@app.route("/process-pdf-fast", methods=["POST"])
def extract_pdf_fast():
    # Check if a file is in the request
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    pdf_file = request.files['pdf']

    # Check if the user has uploaded a file
    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to a temporary directory
    unique_filename = f"{uuid.uuid4()}_{pdf_file.filename}"
    pdf_path = os.path.join(tempFolder, unique_filename)
    pdf_file.save(pdf_path)

    try:
        extracted_json = elements_to_json(pdf_to_elements(pdf_path))
        os.remove(pdf_path)  # Clean up
    except Exception as e:
        os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500

    # Return the extracted text as json
    return extracted_json, 200

@app.route("/process-pdf-advanced", methods=["POST"])
def extract_pdf_advanced():
    # Check if a file is in the request
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    pdf_file = request.files['pdf']

    # Check if the user has uploaded a file
    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to a temporary directory
    unique_filename = f"{uuid.uuid4()}_{pdf_file.filename}"
    pdf_path = os.path.join(tempFolder, unique_filename)
    pdf_file.save(pdf_path)

    try:
        extracted_json = elements_to_json(pdf_to_elements_advanced(pdf_path))
        os.remove(pdf_path)  # Clean up
    except Exception as e:
        os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500

    # Return the extracted text as json
    return extracted_json, 200

app.run(debug=True)