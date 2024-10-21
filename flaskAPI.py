from Preprocessing.PDF.pdfminer import pdf_to_elements
#from Preprocessing.PDF.advanced_pdf import pdf_to_elements_advanced
from flask import Flask, request, jsonify
import json
import uuid
import os

import torch
import detectron2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
import layoutparser as lp

from pdf2image import convert_from_bytes
from PIL import Image

#For Detectron2
import torch
import detectron2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
import layoutparser as lp

import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt

from PIL import Image
import numpy as np
import cv2

import os

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
        os.chdir('..')
        path= ''
        prediction_score_threshold = 0.7
        class_labels = ['text', 'title', 'list', 'table', 'figure']

        # Set up Detectron2 config
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set a threshold for predictions
        cfg.MODEL.WEIGHTS = path+ "model_final.pth" 
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = prediction_score_threshold
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 5

        cfg.MODEL.DEVICE = "cpu"
        
        detected_texts = []

        predictor = DefaultPredictor(cfg)
        
        # Read the file content as bytes
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        if not pdf_file.filename.endswith('.pdf'):
            return {'error': 'Uploaded file is not a PDF'}, 400
        if not pdf_bytes:
            return {'error': 'PDF file is empty'}, 500

        # Convert the PDF into images using `convert_from_bytes`
        images = convert_from_bytes(pdf_bytes)

        images= enumerate(images)
        
        
        for i, current_image in images:
            #img = np.array(Image.open(current_image))
            img = np.array(current_image)

            # Perform page object detection
            outputs = predictor(img)

            # Debug outputs
            instances = outputs["instances"].to("cpu")
            pred_boxes = instances.pred_boxes
            scores = instances.scores
            pred_classes = instances.pred_classes

            # Loop through each detected object
            for i in range(0, len(pred_boxes)):
                box = pred_boxes[i].tensor.numpy()[0]
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])

                # Crop the image to the bounding box
                cropped_img = img[y1:y2, x1:x2]

                # Perform OCR on the cropped image
                text = pytesseract.image_to_string(cropped_img, output_type=Output.STRING)

                # Append the extracted text to the list

                label_key = int(pred_classes[i].numpy())
                label = class_labels[label_key]
                detected_texts.append([label,text.strip()])  # Store each text as a single-element list




     except Exception as e:
        os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500
    
    # Return the extracted text as json
     return json.dumps(detected_texts), 200


# @app.route("/process-pdf-advanced", methods=["POST"])
# def extract_pdf_advanced():
#     # Check if a file is in the request
#     if 'pdf' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     pdf_file = request.files['pdf']

#     # Check if the user has uploaded a file
#     if pdf_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Save the file to a temporary directory
#     unique_filename = f"{uuid.uuid4()}_{pdf_file.filename}"
#     pdf_path = os.path.join(tempFolder, unique_filename)
#     pdf_file.save(pdf_path)

#     try:
#         extracted_json = elements_to_json(pdf_to_elements_advanced(pdf_path))
#         os.remove(pdf_path)  # Clean up
#     except Exception as e:
#         os.remove(pdf_path)
#         return jsonify({"error": str(e)}), 500

#     # Return the extracted text as json
#     return extracted_json, 200



app.run(host="0.0.0.0", port=5000, debug=True)
