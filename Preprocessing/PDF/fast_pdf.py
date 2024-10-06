#For paid version
from unstructured.staging.base import dict_to_elements
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
import unstructured_client

#For free version
from unstructured.partition.auto import partition


def pdf_to_elements_fast_api(pdf_path,unstructured_key,unstructured_url):
    """
    Extracts elements from a pdf file by utilizing the low resolution (fast) pdf extractor from the unstructured.io's API
    
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
        strategy="fast",
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
    
def pdf_to_elements_fast(pdf_path):
    """
    Extracts elements from a pdf file by utilizing the low resolution (fast) pdf extractor without the need of an API
    
    Args:
    pdf_path (String): Path to the pdf file for information extraction.
    
    Returns:
    A list of Unstructured Elements
    """
    try:
        elements = partition(filename=pdf_path,strategy='fast')
        return  elements
    except Exception as e:
        print(e)
        return []
