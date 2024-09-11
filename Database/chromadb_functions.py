from unstructured.chunking.title import chunk_by_title
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import os

def create_database(input_elements, output_db_path):
    try:
        elements = chunk_by_title(input_elements)

        # Create documents from the elements
        documents = []
        for element in elements:
            metadata = element.metadata.to_dict()
            del metadata["languages"]
            metadata["source"] = metadata["filename"]
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
    try:
        embeddings = OpenAIEmbeddings()
        # Initialize Chroma with the directory where the vector store is persisted
        vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

        return vectorstore
    except Exception as e:
        print(f"Error loading database: {e}")
        return None
    
def add_documents_to_database(input_elements, vectorstore):
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
