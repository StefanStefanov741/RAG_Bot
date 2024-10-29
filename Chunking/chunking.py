from Misc.Element import Element

def get_str_after(text, split_str):
    """
    Split on the first occurrence of `split_str` and take everything after it

    Args:
        text (str): The string that the function is going to do the extraction on
        split_str (str): The string or character that the function is going to split the text on

    Returns:
        A string that is part of the text that was taken as input. Taking only the part after the initial split_str found in the text.
    """
    split_index = text.find(split_str)
    
    if split_index != -1:
        # Extract everything after the `split_str`
        return text[split_index + len(split_str):].strip()
    else:
        return text  # Return the whole input if the split_str is not found in it

def character_chunking(input_elements, characterLimit=1000, overlap=0, last_symbol="", last_overlap_symbol=""):
    """
    Chunks elements into groups of text chunks, with each chunk containing up to the specified character limit.
    Allows optional overlap between chunks to repeat characters from the end of one chunk at the start of the next.
    Optionally, chunks end at the last occurrence of a specified symbol before reaching the character limit.

    Args:
        input_elements (list[Element]): A list of Element objects to be chunked based on character limit.
        characterLimit (int): The maximum cumulative character count for each chunk.
        overlap (int, optional): Number of characters to overlap between consecutive chunks.
                                 Defaults to 0 (no overlap).
        last_symbol (str, optional): Character to end chunk on before reaching character limit. 
                                Defaults to "" and if left unchanged it might result into splitting words into different chunks.
                                Set it to "." in order to end on last sentence  (that ends on .), or to " " in order to end on last space. 
        last_overlap_symbol (str, optional): Character to make sure the overlap that is copied to the next chunk is not starting from a cut off word
                                Set it to "." in order to copy as overlap only after the last possible sentence (that ends on .), or to " " in order to start on last space. 

    Returns:
        list[Element]: A list of Element objects representing chunks of text that respect the character limit 
                       (with optional overlap applied).
    """
    output_chunks = []
    current_chunk_text = ""

    for element in input_elements:
        text_to_process = element.text.replace("\xa0", " ")

        while text_to_process:
            # Calculate remaining space
            remaining_space = characterLimit - len(current_chunk_text)
            
            if len(text_to_process) <= remaining_space:
                # If the text fits, add it to the current chunk
                current_chunk_text += text_to_process
                text_to_process = ""
            else:
                # Find last occurrence of `last_symbol` before `remaining_space`
                chunk_text = text_to_process[:remaining_space]
                if last_symbol:
                    last_index = chunk_text.rfind(last_symbol)
                    if last_index != -1:
                        chunk_text = chunk_text[:last_index+1]  # Include the last symbol
                        current_chunk_text += chunk_text
                        text_to_process = text_to_process[len(chunk_text):]
                else:
                    current_chunk_text += chunk_text
                    text_to_process = text_to_process[len(chunk_text):]
                
                # Save the chunk and reset for the next chunk, applying overlap if specified
                output_chunks.append(Element(text=current_chunk_text, category="Chunk"))
                if overlap>0:
                    current_chunk_text = get_str_after(current_chunk_text[-overlap:],last_overlap_symbol)
                else:
                    current_chunk_text = ""
    
    # Append any remaining text in the current chunk
    if current_chunk_text:
        output_chunks.append(Element(text=current_chunk_text, category="Chunk"))

    return output_chunks

def title_chunking(input_elements, characterLimit=1000, overlap=0, last_symbol="", last_overlap_symbol=""):
    """
    Chunks elements into groups of text chunks, with each chunk containing up to the specified character limit. 
    Each chunk starts with the title associated with it.
    Allows optional overlap between chunks to repeat characters from the end of one chunk at the start of the next.
    Optionally, chunks end at the last occurrence of a specified symbol before reaching the character limit.

    Args:
        input_elements (list[Element]): A list of Element objects to be chunked based on character limit.
        characterLimit (int): The maximum cumulative character count for each chunk.
        overlap (int, optional): Number of characters to overlap between consecutive chunks.
                                 Defaults to 0 (no overlap).
        last_symbol (str, optional): Character to end chunk on before reaching character limit. 
                                Defaults to "" and if left unchanged it might result into splitting words into different chunks.
                                Set it to "." in order to end on last sentence  (that ends on .), or to " " in order to end on last space. 
        last_overlap_symbol (str, optional): Character to make sure the overlap that is copied to the next chunk is not starting from a cut off word
                                Set it to "." in order to copy as overlap only after the last possible sentence (that ends on .), or to " " in order to start on last space. 

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
            current_chunk_text = title_text + ": "

        # Process the element's text
        text_to_process = element.text.replace("\xa0", " ")

        if("foods and pollen " in text_to_process):
            a = 1

        while text_to_process:
            # Calculate remaining space
            remaining_space = characterLimit - len(current_chunk_text)
            
            if len(text_to_process) <= remaining_space:
                # Add text if it fits in the current chunk
                if text_to_process + ": " != current_chunk_text:
                    current_chunk_text += text_to_process
                text_to_process = ""
            else:
                # Find last occurrence of `last_symbol` before `remaining_space`
                chunk_text = text_to_process[:remaining_space]
                if last_symbol:
                    last_index = chunk_text.rfind(last_symbol)
                    if last_index != -1:
                        chunk_text = chunk_text[:last_index+1]  # Include the last symbol
                        current_chunk_text += chunk_text
                        text_to_process = text_to_process[len(chunk_text):]
                else:
                    current_chunk_text += chunk_text
                    text_to_process = text_to_process[len(chunk_text):]

                # Save the chunk and reset for the next chunk, applying overlap if specified
                output_chunks.append(Element(text=current_chunk_text, category="Chunk"))
                if overlap>0:
                    current_chunk_text = title_text + ": " + get_str_after(current_chunk_text[-overlap:],last_overlap_symbol)
                else:
                    current_chunk_text = title_text + ": "

    # Append any remaining text in the current chunk
    if current_chunk_text:
        output_chunks.append(Element(text=current_chunk_text, category="Chunk"))

    return output_chunks
