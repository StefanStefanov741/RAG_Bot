from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from typing import Dict, List, Any
from Preprocessing.PDF.fast_pdf import pdf_to_elements_fast
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal
from unstructured.documents.elements import Element, ElementMetadata, CoordinateSystem

"""
In this file, pdfminer is utilized for element extraction from pdfs
"""

def _extract_text_with_layout(pdf_path):
    """
    Extracts text and layout information from a PDF, capturing text along with its position and font size.

    Args:
    pdf_path (str): Path to the PDF file for extracting text and layout information.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries where each dictionary contains text, bounding box (bbox), and font size of the text element.
    """
    text_with_layout = []
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element:
                    text_with_layout.append({
                        'text': text_line.get_text(),
                        'bbox': text_line.bbox,  # (x0, y0, x1, y1)
                        'font_size': text_line._objs[0].size if text_line._objs else None
                    })
    return text_with_layout

def _detect_titles(text_with_layout, title_font_size_threshold=14):
    """
    Detects potential titles in the extracted text based on font size and positioning.

    Args:
    text_with_layout (List[Dict[str, Any]]): List of text elements with layout information (text, bbox, font size).
    title_font_size_threshold (int, optional): The minimum font size considered to identify a title. Default is 14.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries containing title text, bounding box, and font size.
    """
    titles = []
    for item in text_with_layout:
        text = item['text'].strip()
        if text:
            font_size = item['font_size']
            if font_size and font_size >= title_font_size_threshold:
                titles.append({
                    'text': text,
                    'bbox': item['bbox'],
                    'font_size': font_size
                })
    return titles

def _is_string_in_titles(search_string: str, titles: List[Dict[str, Any]]) -> bool:
    """
    Checks if a specific string is present in the list of detected titles.

    Args:
    search_string (str): The string to search for within the titles.
    titles (List[Dict[str, Any]]): List of title elements (text, bbox, font size) identified by `_detect_titles`.

    Returns:
    bool: True if the search string is found within any of the titles, otherwise False.
    """
    search_string = search_string.lower()
    for title in titles:
        if search_string in title['text'].lower():
            return True
    return False

def pdf_to_elements_dict(file_path: str) -> Dict[int, List[Dict[str, Any]]]:
    """
    Extracts text elements from a PDF and organizes them into a dictionary by page number, 
    distinguishing titles from narrative text.

    Args:
    file_path (str): Path to the PDF file.

    Returns:
    Dict[int, List[Dict[str, Any]]]: A dictionary where the keys are page numbers and the values are lists of dictionaries containing text elements (category, text, bbox).
    """
    elements_dict = {}

    titles = _detect_titles(_extract_text_with_layout(file_path))
    
    try:
        for page_number, page_layout in enumerate(extract_pages(file_path), start=1):
            page_elements = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text:
                        x0, y0, x1, y1 = element.bbox
                        if(_is_string_in_titles(titles=titles,search_string=text)):
                            page_elements.append({
                                'category': "Title",
                                'text': text,
                                'bbox': (x0, y0, x1, y1)
                            })
                        else:
                            page_elements.append({
                                'category': "'NarrativeText'",
                                'text': text,
                                'bbox': (x0, y0, x1, y1)
                            })

            if page_elements:
                elements_dict[page_number] = page_elements

    except Exception as e:
        raise

    return elements_dict

def pdf_to_elements(file_path: str) -> List[Element]:
    """
    Extracts text elements from a PDF and returns them as a list of `Element` instances, 
    with metadata such as coordinates, page number, and distinguishing between titles and narrative text.

    Args:
    file_path (str): Path to the PDF file.

    Returns:
    List[Unstructured Element]: A list of `Element` objects representing the text elements in the PDF, with associated metadata such as coordinates and category (title or narrative text).
    """
    extracted_elements = []

    titles = _detect_titles(_extract_text_with_layout(file_path))
    
    try:
        for page_number, page_layout in enumerate(extract_pages(file_path), start=1):
            for page_element in page_layout:
                if isinstance(page_element, LTTextContainer):
                    text = page_element.get_text().strip()
                    if text:
                        x0, y0, x1, y1 = page_element.bbox
                        element_type = "Title" if _is_string_in_titles(search_string=text, titles=titles) else "'NarrativeText'"
                        
                        coordinate_system = CoordinateSystem(
                            width=x1 - x0,
                            height=y1 - y0
                        )
                        
                        metadata = ElementMetadata(
                            filename=file_path,
                            page_number=page_number,
                            coordinates=coordinate_system,
                            languages=['en']
                        )
                        
                        unstructured_element = Element(
                            element_id=None,
                            coordinates=((x0, y0), (x1, y1)),
                            coordinate_system=coordinate_system,
                            metadata=metadata,
                            detection_origin=element_type
                        )

                        unstructured_element.category = element_type
                        unstructured_element.text = text
                        extracted_elements.append(unstructured_element)

    except Exception as e:
        raise

    return extracted_elements