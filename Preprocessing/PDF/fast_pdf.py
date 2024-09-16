#For paid version
from unstructured.staging.base import dict_to_elements
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
import unstructured_client

#For free version
from unstructured.partition.auto import partition


def pdf_to_elements_fast_api(pdf_path,unstructured_key,unstructured_url):
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
        return  dict_to_elements(resp.elements)
    except SDKError as e:
        print(e)
        return []

def pdf_to_elements_fast(pdf_path):
    elements = partition(filename=pdf_path)
    try:
        return  elements
    except Exception as e:
        print(e)
        return []