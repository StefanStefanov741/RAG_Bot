from Preprocessing.PDF.pdfminer import pdf_to_elements
from Preprocessing.PDF.advanced_pdf import pdf_to_elements_advanced,pdf_to_dict_detectron
from flask import Flask, request, jsonify
import json
import uuid
import os
from pdf2image import convert_from_bytes
from PIL import Image



app = Flask(__name__)

tempFolder = "/app/tmp"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Example request - http://localhost:5000/products
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({"message": "Welcome to this API test"}), 200

def elements_to_json(elements):
    # Create a list of dictionaries for each element
    elements_list = [{"category": element.category, "text": element.text} for element in elements]
    
    # Convert the list to a JSON string
    return json.dumps(elements_list, indent=4)

def detectron_array_to_json(array):
    json_output = []

    for item in array:
        # Get category and text from each item in the extracted array
        category, text = item[0], item[1]
        # Create a dictionary for each item and append it to the result list
        json_output.append({"category": category, "text": text.strip()})

    return json.dumps(json_output, indent=4)

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

@app.route("/process-pdf-detectron", methods=["POST"])
def extract_pdf_detectron():
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
        extracted_json = detectron_array_to_json(pdf_to_dict_detectron(pdf_path))
        os.remove(pdf_path)  # Clean up
    except Exception as e:
        os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500

    # Return the extracted text as json
    return extracted_json, 200


@app.route("/process-pdf-yolox", methods=["POST"])
def extract_pdf_yolox():
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



app.run(host="0.0.0.0", port=5000, debug=True)
