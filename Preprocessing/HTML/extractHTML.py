from unstructured.partition.html.partition import partition_html

def html_to_elements(file_path: str):
    """
    Extracts elements from an html file
    
    Args:
    file_path (String): Path to the html file for information extraction.
    
    Returns:
    A list of Unstructured Elements
    """
    return partition_html(filename=file_path)

