from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
import unstructured_client
from unstructured.staging.base import dict_to_elements
from unstructured_inference.inference.layout import DocumentLayout
from unstructured.partition.pdf_image.ocr import process_file_with_ocr
from typing import List

#For free version
from unstructured.partition.auto import partition


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
def pdf_to_elements_advanced(pdf_path):
    """
    Extracts elements from a pdf file by utilizing yolox without the need of an API
    
    Args:
    pdf_path (String): Path to the pdf file for information extraction.
    
    Returns:
    A list of Unstructured Elements
    """
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