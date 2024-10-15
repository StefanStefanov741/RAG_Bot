from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
import unstructured_client
from unstructured.staging.base import dict_to_elements
from unstructured_inference.inference.layout import DocumentLayout
from unstructured.partition.pdf_image.ocr import process_file_with_ocr
from typing import List

#For free version
from unstructured.partition.auto import partition

#For PDF to image conversion, also requires poppler

from pdf2image import convert_from_path
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
import matplotlib as plt

from PIL import Image
import numpy as np
import cv2

def pdf_to_image(path):
    """
    Converts a PDF Document into a list of images     
    Args:
    pdf_path (String): Path to the pdf file for information extraction.

    Returns:
    A list of images (each page is an image) in the format [[1,image1],[2,image2]]
    """
    
    


    # Convert PDF to images
    pdf_path = 'Assets_detectron2/biology_paper.pdf'
    images = convert_from_path(pdf_path)
    return enumerate(images)



def pdf_to_elements_advanced_api(pdf_path,unstructured_key,unstructured_url):
    """
    Extracts elements from a pdf file by utilizing the high resolution (yolox) pdf extractor from the unstructured.io's API
    
    Args:
    pdf_path (String): Path to the pdf file for information extraction.
    unstructured_key (String): The unstructured api key
    unstructured_url (String): The unstructured api url
    
    Returns:
    A list of Unstructured Elements
    """
    u_client = unstructured_client.UnstructuredClient(
        api_key_auth=unstructured_key,
        server_url=unstructured_url
    )

    with open(pdf_path, "rb") as f:
        files=shared.Files(
            content=f.read(),
            file_name=pdf_path,
        )

    req = shared.PartitionParameters(
        files=files,
        strategy="hi_res",
        hi_res_model_name="yolox",
        pdf_infer_table_structure=True,
        skip_infer_table_types=[],
    )

    try:
        resp = u_client.general.partition(req)
        
        #If the element is a table -> save it as html
        i = -1
        for el in resp.elements:
            i+=1
            if(el['type']=='Table'):
                resp.elements[i]['text']=resp.elements[i]['metadata']['text_as_html']

        return  dict_to_elements(resp.elements)
    except SDKError as e:
        print(e)
        return []

#Needs installed poppler and tesseract locally
def pdf_to_elements_advanced(pdf_path, model, display= False) :
    """
    Extracts elements from a pdf file by utilizing yolox without the need of an API
    
    Args:
    pdf_path (String): Path to the pdf file for information extraction.
    
    Returns:
    A list of Unstructured Elements
    """
    
    
    if model == "YoloX":
        try:
            elements = partition(filename=pdf_path,strategy='hi_res',skip_infer_table_types=[])
            i = -1
            for el in elements:
                i+=1
                if(el.category =='Table'):
                    elements[i].text=elements[i].metadata.text_as_html
                if(el.category =='Header'):
                    elements[i].category="Title"
            return  elements
        except Exception as e:
            print(e)
            return []
        
    elif model == "Detectron2":
        
        path= 'Assets_detectron2/'
        prediction_score_threshold = 0.7
        class_labels = ['text', 'title', 'list', 'table', 'figure']

        # Set up Detectron2 config
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set a threshold for predictions
        cfg.MODEL.WEIGHTS = path+ "model_final.pth" # e.g., PubLayNet pre-trained model
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = prediction_score_threshold
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 5

        cfg.MODEL.DEVICE = "cpu"

        # Initialize the OCR library (ensure tesseract is installed and in PATH)
        #pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Update if necessary

        # Initialize an empty list to store the content of each detected object
        detected_texts = []

        predictor = DefaultPredictor(cfg)
        
        images= pdf_to_image(pdf_path)
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


                #print(f"Detected {label}: {text.strip()}")

            if display:

                for i in range(0, len(pred_boxes)):
                    box = pred_boxes[i].tensor.numpy()[0]
                    score = round(float(scores[i].numpy()), 4)
                    label_key = int(pred_classes[i].numpy())
                    label = class_labels[label_key]
                    x = int(box[0])
                    y = int(box[1])
                    w = int(box[2] - box[0])
                    h = int(box[3] - box[1])

                    print('Detected object of label=' + str(label) + ' with score=' + str(score) + ' and in box={x=' + str(x) + ', y=' + str(y) + ', w=' + str(w) + ', h=' + str(h) + '}')
                # Draw the bounding boxes
                for i in range(len(pred_boxes)):
                    box = pred_boxes[i].tensor.numpy()[0]
                    score = round(float(scores[i].numpy()), 4)
                    label_key = int(pred_classes[i].numpy())
                    label = class_labels[label_key]

                    x = int(box[0])
                    y = int(box[1])
                    w = int(box[2] - box[0])
                    h = int(box[3] - box[1])

                    # Draw the rectangle around each object
                    cv2.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)

                    # Put label and score text above the bounding box
                    cv2.putText(img, f"{label}: {score}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Convert the image from BGR to RGB (for matplotlib display)
                image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Display the image with bounding boxes
                plt.figure(figsize=(10, 10))
                plt.imshow(image_rgb)
                plt.axis("off")  # Hide the axis
                plt.show()
        
        return detected_texts
    
    else:
        raise ValueError("Do not recognize the specified model. Choose either YoloX or Detectron2")

