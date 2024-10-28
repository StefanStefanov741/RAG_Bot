from Misc.Element import Element


def character_chunking(input_elements, characterLimit=1000, overlap=0):
    """
    Chunks elements into groups of text chunks, with each chunk containing up to the specified character limit.
    Allows optional overlap between chunks to repeat characters from the end of one chunk at the start of the next.

    Args:
        input_elements (list[Element]): A list of Element objects to be chunked based on character limit.
        characterLimit (int): The maximum cumulative character count for each chunk.
        overlap (int, optional): Number of characters to overlap between consecutive chunks.
                                 Defaults to 0 (no overlap).

    Returns:
        list[Element]: A list of Element objects representing chunks of text that respect the character limit 
                       (with optional overlap applied).
    """
    output_chunks = []
    current_chunk_text = ""
    
    for element in input_elements:
        text_to_process = element.text.replace("\xa0"," ")
        
        while text_to_process:
            # Calculate remaining space, ensuring the current chunk adheres to characterLimit
            remaining_space = characterLimit - len(current_chunk_text)
            
            if len(text_to_process) <= remaining_space:
                # If the text fits, add it to the current chunk
                current_chunk_text += text_to_process
                text_to_process = ""
            else:
                # Add up to the remaining space in the current chunk
                current_chunk_text += text_to_process[:remaining_space]
                text_to_process = text_to_process[remaining_space:]
                
                # Save the chunk and reset for the next chunk, applying overlap if specified
                output_chunks.append(Element(text=current_chunk_text, category="Chunk"))
                
                # Start the next chunk with the overlap portion
                current_chunk_text = current_chunk_text[-overlap:] if overlap > 0 else ""
    
    # Append any remaining text in the current chunk
    if current_chunk_text:
        output_chunks.append(Element(text=current_chunk_text, category="Chunk"))

    return output_chunks

def title_chunking(input_elements, characterLimit=1000, overlap=0):
    """
    Chunks elements into groups of text chunks, with each chunk containing up to the specified character limit. 
    Each chunk starts with the title associated with it.
    Allows optional overlap between chunks to repeat characters from the end of one chunk at the start of the next.

    Args:
        input_elements (list[Element]): A list of Element objects to be chunked based on character limit.
        characterLimit (int): The maximum cumulative character count for each chunk.
        overlap (int, optional): Number of characters to overlap between consecutive chunks.
                                 Defaults to 0 (no overlap).

    Returns:
        list[Element]: A list of Element objects representing chunks of text that respect the character limit 
                       (with optional overlap applied).
    """
    output_chunks = []
    current_chunk_text = ""
    title_text = ""  # Store the last encountered title

    for element in input_elements:
        # Check if the element is a title
        if element.category.lower() == "title":
            # If there's any existing content in the current chunk, save it before starting a new one
            if current_chunk_text:
                output_chunks.append(Element(text=current_chunk_text, category="Chunk"))
                current_chunk_text = ""

            # Begin a new chunk with the title element's text
            title_text = element.text.replace("\xa0", " ")
            current_chunk_text = title_text+": "

        # Process the element's text and ensure it fits within the character limit
        text_to_process = element.text.replace("\xa0", " ")

        while text_to_process:
            # Calculate remaining space
            remaining_space = characterLimit - len(current_chunk_text)
            
            if len(text_to_process) <= remaining_space:
                # Add text if it fits in the current chunk
                if(text_to_process+": "!=current_chunk_text):
                    current_chunk_text += text_to_process
                    
                text_to_process = ""
            else:
                # Add up to the remaining space in the current chunk
                current_chunk_text += text_to_process[:remaining_space]
                text_to_process = text_to_process[remaining_space:]

                # Save the chunk and reset for the next chunk, applying overlap if specified
                output_chunks.append(Element(text=current_chunk_text, category="Chunk"))

                # Start the next chunk with the title and overlap
                current_chunk_text = title_text +": "+ current_chunk_text[-overlap:] if overlap > 0 else title_text+": "

    # Append any remaining text in the current chunk
    if current_chunk_text:
        output_chunks.append(Element(text=current_chunk_text, category="Chunk"))

    return output_chunks