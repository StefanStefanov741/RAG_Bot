from unstructured.chunking.title import chunk_by_title
from unstructured.chunking.basic import chunk_elements
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from Chunking.chunking import character_chunking
from Misc.Element import Element
import os

def create_database(input_elements, output_db_path):
    """
    Creates a chromadb database with the input elements and saves it to the desired location.
    
    Args:
    input_elements (list(Unstructured Element)): The list of extracted elements from the input files that should be saved in the vectorstore
    output_db_path (String): The path to the folder where the vectorstore should be created
    
    Returns:
    True if it successfully created the vectorstore in the desired location.
    False if there was an issue.
    """
    try:
        elements = chunk_by_title(elements=input_elements,overlap=True)
        #elements = chunk_elements(elements=input_elements,max_characters=99999,overlap=True)

        # Create documents from the elements
        documents = []
        for element in elements:
            metadata = element.metadata.to_dict()
            del metadata["languages"]
            metadata["source"] = metadata["filename"]
            # Remove metadata items that are lists
            keys_to_remove = [key for key, value in metadata.items() if isinstance(value, list)]
            for key in keys_to_remove:
                del metadata[key]

            documents.append(Document(page_content=element.text, metadata=metadata))

        embeddings = OpenAIEmbeddings()

        # Create a vector db from the documents and specify the directory for persistence
        vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=output_db_path)
        vectorstore.persist()  # Persist the vector store to disk
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
def load_database_from_dir(db_path):
    """
    Loads the vectorstore to a variable by providing the path to the folder containing it.
    
    Args:
    db_path (String): Path to the folder, where the vectorstore was saved.
    
    Returns:
    A reference to the vectorstore found and the specified location.
    """
    try:
        embeddings = OpenAIEmbeddings()
        # Initialize Chroma with the directory where the vector store is persisted
        vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

        return vectorstore
    except Exception as e:
        print(f"Error loading database: {e}")
        return None
    
def add_documents_to_database(input_elements, vectorstore):
    """
    Adds new elements to an already existing vectorstore
    
    Args:
    input_elements (list(Unstructured Element)): The list of extracted elements from the input files that should be saved in the vectorstore
    vectorstore (Chroma): A reference to the chromadb vectorstore that should aquire the new elements.
    
    Returns:
    True if success
    False if failed
    """
    try:
        # Chunk the input elements and create documents
        elements = chunk_by_title(input_elements)
        new_documents = []
        for element in elements:
            metadata = element.metadata.to_dict()
            del metadata["languages"]
            metadata["source"] = metadata["filename"]
            new_documents.append(Document(page_content=element.text, metadata=metadata))
        
        # Add new documents to the existing vector store
        vectorstore.add_documents(new_documents)
        
        # Persist the updated vector store
        vectorstore.persist()
        
        print("Documents added and database successfully updated.")
        return True
    except Exception as e:
        print(f"Error adding documents to database: {e}")
        return False

def create_database2(input_elements, output_db_path):
    """
    Creates a chromadb database with the input Misc.Element elements and saves it to the desired location.
    
    Args:
    input_elements (list(Misc.Element)): The list of extracted elements from the input files that should be saved in the vectorstore
    output_db_path (String): The path to the folder where the vectorstore should be created
    
    Returns:
    True if it successfully created the vectorstore in the desired location.
    False if there was an issue.
    """
    try:
        elements = character_chunking(input_elements=input_elements,characterLimit=1000,overlap=100)
        #elements = chunk_elements(elements=input_elements,max_characters=99999,overlap=True)

        # Create documents from the elements
        documents = []
        for element in elements:
            documents.append(Document(page_content=element.text, metadata=element.return_metadata()))

        embeddings = OpenAIEmbeddings()

        # Create a vector db from the documents and specify the directory for persistence
        vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=output_db_path)
        vectorstore.persist()  # Persist the vector store to disk
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
def add_documents_to_database2(input_elements, vectorstore):
    """
    Adds new Misc.Element elements to an already existing vectorstore
    
    Args:
    input_elements (list(Misc.Element)): The list of extracted elements from the input files that should be saved in the vectorstore
    vectorstore (Chroma): A reference to the chromadb vectorstore that should aquire the new elements.
    
    Returns:
    True if success
    False if failed
    """
    try:
        # Chunk the input elements and create documents
        elements = character_chunking(input_elements=input_elements,characterLimit=1000,overlap=100)
        new_documents = []
        for element in elements:
            new_documents.append(Document(page_content=element.text, metadata=element.return_metadata()))
        
        # Add new documents to the existing vector store
        vectorstore.add_documents(new_documents)
        
        # Persist the updated vector store
        vectorstore.persist()
        
        print("Documents added and database successfully updated.")
        return True
    except Exception as e:
        print(f"Error adding documents to database: {e}")
        return False